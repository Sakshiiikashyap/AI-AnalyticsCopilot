from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.chat import service
from app.features.chat.schemas import (
    ChatMessageResponse,
    ChatSessionResponse,
    CreateChatSessionRequest,
    SendMessageRequest,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_session(
    payload: CreateChatSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_session(db, str(current_user.id), str(payload.dataset_id))


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def list_messages(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = service.list_messages(db, str(current_user.id), session_id)
    return [
        ChatMessageResponse(
            id=m.id, role=m.role, content=m.content, computed_context=m.computed_context_json, created_at=m.created_at
        )
        for m in messages
    ]


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=201)
def send_message(
    session_id: str,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = service.send_message(db, str(current_user.id), session_id, payload.content)
    return ChatMessageResponse(
        id=msg.id, role=msg.role, content=msg.content, computed_context=msg.computed_context_json, created_at=msg.created_at
    )