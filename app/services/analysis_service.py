from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import EvaluationResult, ExperimentRun


class AnalysisService:
    def __init__(self, session: Session):
        self.session = session

    def list_run_summaries(self) -> List[Dict]:
        stmt = (
            select(
                ExperimentRun.id,
                ExperimentRun.run_name,
                ExperimentRun.experiment_id,
                ExperimentRun.sample_total,
                ExperimentRun.sample_completed,
                ExperimentRun.avg_overall_score,
                ExperimentRun.avg_correctness,
                ExperimentRun.avg_groundedness,
                ExperimentRun.avg_hallucination_risk,
                ExperimentRun.run_status,
            )
            .order_by(ExperimentRun.created_at.desc())
        )
        rows = self.session.execute(stmt).all()
        return [
            {
                "run_id": row[0],
                "run_name": row[1],
                "experiment_id": row[2],
                "sample_total": row[3],
                "sample_completed": row[4],
                "avg_overall_score": row[5],
                "avg_correctness": row[6],
                "avg_groundedness": row[7],
                "avg_hallucination_risk": row[8],
                "status": row[9],
            }
            for row in rows
        ]

    def overview(self) -> Dict:
        total_runs = self.session.scalar(select(func.count(ExperimentRun.id))) or 0
        total_results = self.session.scalar(select(func.count(EvaluationResult.id))) or 0
        avg_score = self.session.scalar(select(func.avg(EvaluationResult.overall_score))) or 0.0
        avg_hallucination = self.session.scalar(select(func.avg(EvaluationResult.hallucination_risk))) or 0.0
        return {
            "total_runs": int(total_runs),
            "total_results": int(total_results),
            "avg_overall_score": round(float(avg_score), 4),
            "avg_hallucination_risk": round(float(avg_hallucination), 4),
        }
