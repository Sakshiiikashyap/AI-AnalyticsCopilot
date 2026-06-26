from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.main import limiter
from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth import service
from app.features.auth.models import User
from app.features.auth.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    user = service.signup(db, payload)
    access, refresh = service.issue_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = service.authenticate(db, payload)
    access, refresh = service.issue_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    new_access = service.refresh_access_token(payload.refresh_token)
    return TokenResponse(access_token=new_access, refresh_token=payload.refresh_token)


@router.post("/password-reset/request", status_code=202)
@limiter.limit("3/minute")
def request_password_reset(request: Request, payload: PasswordResetRequest, db: Session = Depends(get_db)):
    service.request_password_reset(db, payload.email)
    return {"message": "If an account exists for this email, a reset link has been sent."}


@router.post("/password-reset/confirm", status_code=200)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    service.confirm_password_reset(db, payload.token, payload.new_password)
    return {"message": "Password has been reset successfully."}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
