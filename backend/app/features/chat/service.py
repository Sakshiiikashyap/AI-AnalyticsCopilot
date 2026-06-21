from sqlalchemy.orm import Session

from app.features.chat import query_engine
from app.features.chat.models import ChatMessage, ChatSession
from app.features.datasets.models import Dataset
from app.features.datasets.service import get_dataframe_for_dataset, get_dataset
from app.features.profiling.models import DatasetProfile
from app.llm.factory import get_llm_provider
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.shared.exceptions import NotFoundError, UpstreamError, parse_uuid


def create_session(db: Session, user_id: str, dataset_id: str) -> ChatSession:
    get_dataset(db, user_id, dataset_id)
    session = ChatSession(dataset_id=parse_uuid(dataset_id, "dataset"), user_id=parse_uuid(user_id, "user"))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, user_id: str, session_id: str) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == parse_uuid(session_id, "chat session"), ChatSession.user_id == parse_uuid(user_id, "user"))
        .first()
    )
    if not session:
        raise NotFoundError("Chat session not found.")
    return session


def list_messages(db: Session, user_id: str, session_id: str):
    session = get_session(db, user_id, session_id)
    return session.messages


def send_message(db: Session, user_id: str, session_id: str, content: str) -> ChatMessage:
    session = get_session(db, user_id, session_id)

    user_msg = ChatMessage(session_id=session.id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    dataset: Dataset = get_dataset(db, user_id, str(session.dataset_id))
    profile = db.query(DatasetProfile).filter(DatasetProfile.dataset_id == dataset.id).first()
    profile_dict = None
    if profile:
        profile_dict = {
            "summary": profile.summary_json,
            "duplicates_count": profile.duplicates_count,
            "correlation": profile.correlation_json,
            "outliers": profile.outliers_json,
        }

    df = get_dataframe_for_dataset(dataset)
    computed_result = query_engine.try_compute(content, df)

    user_prompt = build_user_prompt(
        question=content,
        schema=dataset.schema_json or {},
        profile=profile_dict,
        computed_result=computed_result,
    )

    llm = get_llm_provider()
    try:
        answer_text = llm.generate(SYSTEM_PROMPT, user_prompt)
    except Exception:
        raise UpstreamError("The AI service is temporarily unavailable. Please try again in a moment.")

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer_text,
        computed_context_json=computed_result,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return assistant_msg