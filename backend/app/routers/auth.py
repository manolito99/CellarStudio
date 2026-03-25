from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import login, refresh_access_token
from app.utils.security import hash_password, verify_password

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


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    if len(body.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 6 caracteres",
        )
    current_user.password_hash = hash_password(body.new_password)
    db.commit()
