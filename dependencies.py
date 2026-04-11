from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import Settings, get_settings
from db.session import get_db
from models.user import User
from repositories.user_repo import UserRepo
from services.auth_service import AuthService

# auto_error=False: /login は JSON を受け付けるため Swagger UI の Authorize ボタンとは形式が異なる。
# Bearer トークンの検証は get_current_user 内で手動で行う。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """JWT を検証し、現在のユーザーを返す FastAPI dependency。"""
    if token is None:
        raise HTTPException(status_code=401, detail="認証トークンがありません。")
    auth_svc = AuthService(db, settings)
    user_id = auth_svc.decode_token(token)
    user = UserRepo(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="ユーザーが見つかりません。")
    return user
