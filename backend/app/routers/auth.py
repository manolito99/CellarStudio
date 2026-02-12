from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import login, refresh_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def auth_login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    return login(db, body.email, body.password)


@router.post("/refresh", response_model=TokenResponse)
def auth_refresh(body: RefreshRequest, db: Annotated[Session, Depends(get_db)]):
    return refresh_access_token(db, body.refresh_token)


@router.get("/me", response_model=UserResponse)
def auth_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
