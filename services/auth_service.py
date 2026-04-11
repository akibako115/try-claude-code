from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import Settings
from repositories.user_repo import UserRepo
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._repo = UserRepo(db)
        self._db = db
        self._settings = settings

    def register(self, req: RegisterRequest) -> UserOut:
        if self._repo.exists_by_email(req.email):
            raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています。")
        user = self._repo.create(
            email=req.email,
            username=req.username,
            hashed_password=_hash_password(req.password),
        )
        self._db.commit()
        self._db.refresh(user)
        return UserOut.model_validate(user)

    def login(self, req: LoginRequest) -> TokenResponse:
        user = self._repo.get_by_email(req.email)
        if user is None or not _verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません。")
        token = self._create_access_token(user.id)
        return TokenResponse(access_token=token)

    def decode_token(self, token: str) -> int:
        """JWT を検証してユーザーIDを返す。不正なトークンは 401 を送出する。"""
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
            )
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="無効なトークンです。")
            return int(user_id)
        except JWTError:
            raise HTTPException(status_code=401, detail="無効なトークンです。")

    def _create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.access_token_expire_minutes
        )
        return jwt.encode(
            {"sub": str(user_id), "exp": expire},
            self._settings.secret_key,
            algorithm=self._settings.algorithm,
        )
