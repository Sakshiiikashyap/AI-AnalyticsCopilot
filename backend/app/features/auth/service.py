from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.features.auth.models import User
from app.features.auth.schemas import LoginRequest, SignupRequest
from app.shared.exceptions import ConflictError, UnauthorizedError


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