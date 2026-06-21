import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CreateChatSessionRequest(BaseModel):
    dataset_id: uuid.UUID


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    computed_context: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}