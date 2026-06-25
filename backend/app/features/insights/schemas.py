import uuid
from datetime import datetime

from pydantic import BaseModel


class InsightResponse(BaseModel):
    dataset_id: uuid.UUID
    summary: str
    key_findings: list[str]
    risks: list[str]
    opportunities: list[str]
    recommendations: list[str]
    generated_at: datetime