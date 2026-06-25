import uuid
from typing import Any

from pydantic import BaseModel


class AnomalyDetectionRequest(BaseModel):
    method: str = "isolation_forest"
    contamination: float = 0.05


class AnomalyRecord(BaseModel):
    row_index: int
    anomaly_score: float
    row_data: dict[str, Any]


class AnomalyResponse(BaseModel):
    dataset_id: uuid.UUID
    method: str
    columns_used: list[str]
    total_rows: int
    anomaly_count: int
    anomalies: list[AnomalyRecord]