from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class MetricScores(BaseModel):
    correctness: float = 0.0
    completeness: float = 0.0
    groundedness: float = 0.0
    format_compliance: float = 0.0
    hallucination_risk: float = 0.0
    overall_score: float = 0.0


class BadcaseTagRead(BaseModel):
    id: int
    code: str
    name: str
    description: str
    severity: str

    model_config = {"from_attributes": True}


class EvaluationResultRead(MetricScores):
    id: int
    experiment_run_id: int
    sample_id: int
    generated_answer: str
    rendered_prompt: str
    judge_detail: Dict = Field(default_factory=dict)
    is_bad_case: bool = False
    badcase_tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RunSummaryRead(BaseModel):
    run_id: int
    run_name: str
    experiment_id: int
    sample_total: int
    sample_completed: int
    avg_overall_score: float
    avg_correctness: float
    avg_groundedness: float
    avg_hallucination_risk: float
    status: str
