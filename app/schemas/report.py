from typing import Dict, Literal

from pydantic import BaseModel


class ReportCompareRequest(BaseModel):
    dataset_id: int
    prompt_version_a_id: int
    prompt_version_b_id: int
    output_format: Literal["markdown", "html"] = "markdown"


class ReportExportResponse(BaseModel):
    filename: str
    content_type: str
    content: str
    summary: Dict
