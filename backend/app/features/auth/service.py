import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.features.auth.models import PasswordResetToken, User
from app.features.auth.schemas import LoginRequest, SignupRequest
from app.shared.exceptions import ConflictError, NotFoundError, UnauthorizedError, parse_uuid


def signup(db: Session, payload: SignupRequest) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ConflictError("An account with this email already exists.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, payload: LoginRequest) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password.")
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    user_id = str(user.id)
    return create_access_token(user_id), create_refresh_token(user_id)


def refresh_access_token(refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid or expired refresh token.")
    return create_access_token(payload["sub"])


def get_user_by_id(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == parse_uuid(user_id, "user")).first()
    if not user:
        raise NotFoundError("User not found.")
    return user


def request_password_reset(db: Session, email: str) -> str | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    raw_token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        user_id=user.id,
        token=raw_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()
    return raw_token


def confirm_password_reset(db: Session, token: str, new_password: str) -> None:
    reset = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not reset or reset.used or reset.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedError("Invalid or expired reset token.")

    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise NotFoundError("User not found.")

    user.hashed_password = hash_password(new_password)
    reset.used = True
    db.commit()
