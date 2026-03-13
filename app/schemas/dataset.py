from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    name: str
    description: str = ""
    source_type: str = "manual"
    source_path: str = ""
    status: str = "active"


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_path: Optional[str] = None
    status: Optional[str] = None


class DatasetRead(DatasetBase):
    id: int
    sample_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SampleBase(BaseModel):
    query: str
    context: str
    reference_answer: str
    category: str
    difficulty: str = "medium"
    tags: List[str] = Field(default_factory=list)
    notes: str = ""


class SampleCreate(SampleBase):
    pass


class SampleUpdate(BaseModel):
    query: Optional[str] = None
    context: Optional[str] = None
    reference_answer: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class SampleRead(SampleBase):
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetImportRequest(BaseModel):
    dataset_id: int
    file_path: str
