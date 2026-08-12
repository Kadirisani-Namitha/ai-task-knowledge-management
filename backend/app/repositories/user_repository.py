from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self._db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.scalar(stmt)

    def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self._db.scalars(stmt).all())

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self._db.delete(user)
        self._db.commit()
