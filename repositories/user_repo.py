from __future__ import annotations

from sqlalchemy.orm import Session

from models.user import User


class UserRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.query(User).filter(User.id == user_id).first()

    def exists_by_email(self, email: str) -> bool:
        return self._db.query(User.id).filter(User.email == email).first() is not None

    def create(self, email: str, username: str, hashed_password: str) -> User:
        user = User(email=email, username=username, hashed_password=hashed_password)
        self._db.add(user)
        self._db.flush()
        return user
