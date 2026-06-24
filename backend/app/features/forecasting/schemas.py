import uuid
from typing import Any

from pydantic import BaseModel


class ForecastRequest(BaseModel):
    date_column: str | None = None
    metric_column: str | None = None
    periods: int = 30


class ForecastResponse(BaseModel):
    dataset_id: uuid.UUID
    date_column: str
    metric_column: str
    method: str
    frequency: str
    history: list[dict[str, Any]]
    forecast: list[dict[str, Any]]
    backtest: dict[str, Any] | None = None
    warning: str | None = None