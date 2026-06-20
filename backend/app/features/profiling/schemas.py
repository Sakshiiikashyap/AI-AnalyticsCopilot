import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DatasetProfileResponse(BaseModel):
    dataset_id: uuid.UUID
    summary: dict[str, Any]
    missing_values: dict[str, Any]
    duplicates_count: int
    correlation: dict[str, Any]
    outliers: dict[str, Any]
    generated_at: datetime