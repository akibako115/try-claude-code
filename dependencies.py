from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import Settings, get_settings
from db.session import get_db
from models.user import User
from repositories.user_repo import UserRepo
from services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """JWT を検証し、現在のユーザーを返す FastAPI dependency。"""
    auth_svc = AuthService(db, settings)
    user_id = auth_svc.decode_token(token)
    user = UserRepo(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="ユーザーが見つかりません。")
    return user
