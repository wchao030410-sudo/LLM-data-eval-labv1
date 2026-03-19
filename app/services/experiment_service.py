from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Dataset, EvaluationResult, Experiment, ExperimentRun, PromptVersion
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate
from app.services.badcase_service import BadcaseService
from app.services.benchmark_service import BenchmarkService
from app.services.dataset_service import DatasetService
from app.services.evaluation_service import Evaluator
from app.services.llm_client import ModelClient
from app.services.prompt_service import PromptService
from app.utils.scoring import average_metric
from app.utils.internal_data import HIDDEN_DATASET_STATUS


class ExperimentService:
    def __init__(self, session: Session):
        self.session = session
        self.dataset_service = DatasetService(session)
        self.prompt_service = PromptService(session)
        self.evaluator = Evaluator()
        self.benchmark_service = BenchmarkService()
        self.badcase_service = BadcaseService(session)
        self.model_client = ModelClient()

    def create_experiment(self, payload: ExperimentCreate) -> Experiment:
        experiment = Experiment(**payload.model_dump())
        self.session.add(experiment)
        self.session.flush()
        return experiment

    def list_experiments(self) -> List[Experiment]:
        stmt = (
            select(Experiment)
            .join(Dataset, Dataset.id == Experiment.dataset_id)
            .where(Dataset.status != HIDDEN_DATASET_STATUS)
            .order_by(Experiment.created_at.desc())
        )
        return list(self.session.scalars(stmt))

    def get_experiment(self, experiment_id: int) -> Optional[Experiment]:
        stmt = (
            select(Experiment)
            .options(
                selectinload(Experiment.dataset),
                selectinload(Experiment.prompt_version).selectinload(PromptVersion.prompt),
                selectinload(Experiment.runs),
            )
            .where(Experiment.id == experiment_id)
        )
        return self.session.scalars(stmt).first()

    def update_experiment(self, experiment_id: int, payload: ExperimentUpdate) -> Experiment:
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(experiment, key, value)
        self.session.flush()
        return experiment

    def list_runs(self) -> List[ExperimentRun]:
        stmt = (
            select(ExperimentRun)
            .join(Experiment, Experiment.id == ExperimentRun.experiment_id)
            .join(Dataset, Dataset.id == Experiment.dataset_id)
            .where(Dataset.status != HIDDEN_DATASET_STATUS)
            .order_by(ExperimentRun.created_at.desc())
        )
        return list(self.session.scalars(stmt))

    def get_run(self, run_id: int) -> Optional[ExperimentRun]:
        stmt = (
            select(ExperimentRun)
            .options(selectinload(ExperimentRun.evaluation_results).selectinload(EvaluationResult.tag_links))
            .where(ExperimentRun.id == run_id)
        )
        return self.session.scalars(stmt).first()

    def get_results(self, run_id: int) -> List[Dict]:
        stmt = (
            select(EvaluationResult)
            .options(selectinload(EvaluationResult.tag_links))
            .where(EvaluationResult.experiment_run_id == run_id)
            .order_by(EvaluationResult.overall_score.asc(), EvaluationResult.id.asc())
        )
        results = self.session.scalars(stmt).all()
        serialized = []
        for result in results:
            serialized.append(
                {
                    "id": result.id,
                    "experiment_run_id": result.experiment_run_id,
                    "sample_id": result.sample_id,
                    "generated_answer": result.generated_answer,
                    "rendered_prompt": result.rendered_prompt,
                    "correctness": result.correctness,
                    "completeness": result.completeness,
                    "groundedness": result.groundedness,
                    "format_compliance": result.format_compliance,
                    "hallucination_risk": result.hallucination_risk,
                    "overall_score": result.overall_score,
                    "judge_detail": result.judge_detail,
                    "is_bad_case": result.is_bad_case,
                    "badcase_tags": [link.badcase_tag.code for link in result.tag_links],
                    "created_at": result.created_at,
                    "updated_at": result.updated_at,
                }
            )
        return serialized

    def run_experiment(self, experiment_id: int, run_name: Optional[str] = None) -> ExperimentRun:
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")

        samples = self.dataset_service.list_samples(experiment.dataset_id)
        if not samples:
            raise ValueError("Dataset has no samples")

        self.badcase_service.ensure_default_tags()

        run = ExperimentRun(
            experiment_id=experiment.id,
            run_name=run_name or "{name}-{ts}".format(name=experiment.name, ts=datetime.utcnow().strftime("%Y%m%d%H%M%S")),
            run_status="running",
            started_at=datetime.utcnow(),
            sample_total=len(samples),
            sample_completed=0,
        )
        experiment.status = "running"
        self.session.add(run)
        self.session.flush()

        metric_records = []
        try:
            for sample in samples:
                messages, rendered_prompt = self.prompt_service.render_prompt(experiment.prompt_version, sample)
                generation = self.model_client.generate_answer(
                    messages=messages,
                    model_name=experiment.target_model,
                    temperature=experiment.temperature,
                    max_tokens=experiment.max_tokens,
                )
                generated_answer = generation["text"]
                scores = self.evaluator.evaluate(sample, generated_answer)
                benchmark_context = self.benchmark_service.build_context(sample, generated_answer, scores)
                judge_detail = {
                    "generation_mode": generation["mode"],
                    "judge_mode": experiment.judge_mode,
                    **benchmark_context,
                }
                if experiment.judge_mode == "llm_judge":
                    judge_prompt = self.evaluator.build_judge_prompt(
                        sample,
                        generated_answer,
                        benchmark_focus=self.benchmark_service.review_focus(benchmark_context),
                    )
                    judge_detail["llm_judge"] = self.model_client.judge_answer(judge_prompt, model_name=experiment.target_model)

                result = EvaluationResult(
                    experiment_run_id=run.id,
                    sample_id=sample.id,
                    generated_answer=generated_answer,
                    rendered_prompt=rendered_prompt,
                    judge_detail=judge_detail,
                    **scores
                )
                self.session.add(result)
                self.session.flush()

                tag_codes = self.badcase_service.infer_tag_codes(sample, generated_answer, scores)
                attached_codes = self.badcase_service.attach_tags(result, tag_codes)
                result.judge_detail["badcase_tags"] = attached_codes
                run.sample_completed += 1
                metric_records.append(scores)

            run.avg_overall_score = average_metric(metric_records, "overall_score")
            run.avg_correctness = average_metric(metric_records, "correctness")
            run.avg_groundedness = average_metric(metric_records, "groundedness")
            run.avg_hallucination_risk = average_metric(metric_records, "hallucination_risk")
            run.run_status = "completed"
            run.finished_at = datetime.utcnow()
            experiment.status = "completed"
            self.session.flush()
            return run
        except Exception as exc:
            run.run_status = "failed"
            run.finished_at = datetime.utcnow()
            run.error_message = str(exc)
            experiment.status = "failed"
            self.session.flush()
            raise
