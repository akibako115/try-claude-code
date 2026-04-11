from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import Settings, get_settings
from db.session import get_db
from dependencies import get_current_user
from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UserOut:
    """新規ユーザーを登録する。"""
    return AuthService(db, settings).register(req)


@router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """ログインして JWT アクセストークンを取得する。"""
    return AuthService(db, settings).login(req)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """現在ログイン中のユーザー情報を返す。"""
    return UserOut.model_validate(current_user)
