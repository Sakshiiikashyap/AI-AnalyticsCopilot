import uuid
from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}