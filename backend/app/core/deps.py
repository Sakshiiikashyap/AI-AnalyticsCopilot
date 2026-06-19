import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.features.auth.models import User
from app.shared.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Not authenticated.")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Invalid or expired token.")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise UnauthorizedError("Invalid token subject.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedError("User no longer exists.")
    return user