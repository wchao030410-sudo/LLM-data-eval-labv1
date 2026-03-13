from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PromptBase(BaseModel):
    name: str
    description: str = ""
    task_type: str = "search_qa"
    owner: str = "portfolio"


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    owner: Optional[str] = None


class PromptRead(PromptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptVersionBase(BaseModel):
    version: str
    system_prompt: str = ""
    user_prompt_template: str
    few_shot_examples: List[Dict] = Field(default_factory=list)
    variables_schema: Dict = Field(default_factory=dict)
    change_note: str = ""
    is_active: bool = True


class PromptVersionCreate(PromptVersionBase):
    prompt_id: int


class PromptVersionUpdate(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    few_shot_examples: Optional[List[Dict]] = None
    variables_schema: Optional[Dict] = None
    change_note: Optional[str] = None
    is_active: Optional[bool] = None


class PromptVersionRead(PromptVersionBase):
    id: int
    prompt_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
