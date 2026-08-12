import logging
from sqlalchemy.orm import Session

from app.models.models import User, RoleName
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.schemas.schemas import UserCreate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)

    def register_user(self, payload: UserCreate) -> User:
        # Check if username or email already exists
        if self._repo.get_by_username(payload.username):
            raise ValueError("Username already registered")
        if self._repo.get_by_email(payload.email):
            raise ValueError("Email already registered")

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role_id=payload.role_id,
            is_active=True,
        )
        return self._repo.create(user)

    def list_users(self, current_user: User) -> list[User]:
        # Admins can list all users to assign tasks
        if current_user.role.name != RoleName.ADMIN:
            raise PermissionError("Access denied: Admin role required to list users")
        return self._repo.list_users()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self._repo.get_by_id(user_id)
