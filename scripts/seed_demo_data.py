import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import engine, get_session
from app.models import Base, Dataset, EvaluationResult, EvaluationResultBadcaseTag, Experiment, ExperimentRun, Prompt, PromptVersion
from app.schemas.dataset import DatasetCreate, SampleCreate
from app.schemas.prompt import PromptCreate, PromptVersionCreate
from app.services.badcase_service import BadcaseService
from app.services.dataset_service import DatasetService
from app.services.prompt_service import PromptService
from app.utils.demo_data import get_demo_prompts, get_demo_samples


LEGACY_DATASET_NAMES = {"demo_search_qa"}
LEGACY_PROMPT_NAMES = {"search_qa_baseline", "search_qa_structured", "search_qa_strict_json"}


def cleanup_legacy_demo() -> None:
    with get_session() as session:
        legacy_dataset_ids = {item.id for item in session.query(Dataset).filter(Dataset.name.in_(LEGACY_DATASET_NAMES)).all()}
        legacy_prompt_ids = {item.id for item in session.query(Prompt).filter(Prompt.name.in_(LEGACY_PROMPT_NAMES)).all()}
        legacy_version_ids = {item.id for item in session.query(PromptVersion).filter(PromptVersion.prompt_id.in_(legacy_prompt_ids)).all()}

        legacy_experiment_ids = {
            item.id for item in session.query(Experiment).filter(
                (Experiment.dataset_id.in_(legacy_dataset_ids)) | (Experiment.prompt_version_id.in_(legacy_version_ids))
            ).all()
        }
        legacy_run_ids = {item.id for item in session.query(ExperimentRun).filter(ExperimentRun.experiment_id.in_(legacy_experiment_ids)).all()}
        legacy_result_ids = {
            item.id for item in session.query(EvaluationResult).filter(EvaluationResult.experiment_run_id.in_(legacy_run_ids)).all()
        }

        if legacy_result_ids:
            session.query(EvaluationResultBadcaseTag).filter(
                EvaluationResultBadcaseTag.evaluation_result_id.in_(legacy_result_ids)
            ).delete(synchronize_session=False)
            session.query(EvaluationResult).filter(EvaluationResult.id.in_(legacy_result_ids)).delete(synchronize_session=False)

        if legacy_run_ids:
            session.query(ExperimentRun).filter(ExperimentRun.id.in_(legacy_run_ids)).delete(synchronize_session=False)

        if legacy_experiment_ids:
            session.query(Experiment).filter(Experiment.id.in_(legacy_experiment_ids)).delete(synchronize_session=False)

        if legacy_version_ids:
            session.query(PromptVersion).filter(PromptVersion.id.in_(legacy_version_ids)).delete(synchronize_session=False)

        if legacy_prompt_ids:
            session.query(Prompt).filter(Prompt.id.in_(legacy_prompt_ids)).delete(synchronize_session=False)

        for dataset in session.query(Dataset).filter(Dataset.id.in_(legacy_dataset_ids)).all():
            session.delete(dataset)


def seed_dataset() -> None:
    with get_session() as session:
        dataset_service = DatasetService(session)
        existing = session.query(Dataset).filter(Dataset.name == "中文搜索问答演示集").first()
        if existing:
            return
        dataset = dataset_service.create_dataset(
            DatasetCreate(
                name="中文搜索问答演示集",
                description="用于演示 Search QA 评测流程的中文样本集。",
                source_type="demo",
                source_path="generated://zh_search_qa_demo",
                status="active",
            )
        )
        payloads = [SampleCreate(**item) for item in get_demo_samples()]
        dataset_service.bulk_create_samples(dataset.id, payloads)


def seed_prompts() -> None:
    with get_session() as session:
        prompt_service = PromptService(session)
        existing_names = {prompt.name for prompt in session.query(Prompt).all()}
        for prompt_data in get_demo_prompts():
            if prompt_data["name"] in existing_names:
                continue
            prompt = prompt_service.create_prompt(
                PromptCreate(
                    name=prompt_data["name"],
                    description=prompt_data["description"],
                    task_type=prompt_data["task_type"],
                    owner=prompt_data["owner"],
                )
            )
            for version in prompt_data["versions"]:
                prompt_service.create_prompt_version(
                    PromptVersionCreate(
                        prompt_id=prompt.id,
                        version=version["version"],
                        system_prompt=version["system_prompt"],
                        user_prompt_template=version["user_prompt_template"],
                        few_shot_examples=version["few_shot_examples"],
                        variables_schema=version["variables_schema"],
                        change_note=version["change_note"],
                        is_active=version["is_active"],
                    )
                )


def seed_badcase_tags() -> None:
    with get_session() as session:
        BadcaseService(session).ensure_default_tags()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    cleanup_legacy_demo()
    seed_badcase_tags()
    seed_dataset()
    seed_prompts()
    print("Seed completed.")


if __name__ == "__main__":
    main()
