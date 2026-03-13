from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ExperimentBase(BaseModel):
    name: str
    description: str = ""
    dataset_id: int
    prompt_version_id: int
    target_model: str
    temperature: float = 0.2
    top_p: float = 1.0
    max_tokens: int = 512
    judge_mode: str = "rule"
    status: str = "draft"


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataset_id: Optional[int] = None
    prompt_version_id: Optional[int] = None
    target_model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    judge_mode: Optional[str] = None
    status: Optional[str] = None


class ExperimentRead(ExperimentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExperimentRunRequest(BaseModel):
    run_name: Optional[str] = None


class ExperimentRunRead(BaseModel):
    id: int
    experiment_id: int
    run_name: str
    run_status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    sample_total: int
    sample_completed: int
    avg_overall_score: float
    avg_correctness: float
    avg_groundedness: float
    avg_hallucination_risk: float
    error_message: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
