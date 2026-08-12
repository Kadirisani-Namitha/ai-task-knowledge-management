from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Role


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, role_id: int) -> Role | None:
        return self._db.get(Role, role_id)

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self._db.scalar(stmt)

    def list_roles(self) -> list[Role]:
        stmt = select(Role)
        return list(self._db.scalars(stmt).all())

    def create(self, role: Role) -> Role:
        self._db.add(role)
        self._db.commit()
        self._db.refresh(role)
        return role
