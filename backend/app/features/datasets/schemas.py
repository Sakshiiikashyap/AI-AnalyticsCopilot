import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    original_filename: str
    file_type: str
    row_count: int | None
    column_count: int | None
    schema_json: dict[str, Any] | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetPreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int