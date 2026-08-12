import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin, get_current_user
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserCreate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    """Get details of the currently logged-in user."""
    return UserResponse.model_validate(current_user)


@router.get("", response_model=list[UserResponse])
def list_users(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> list[UserResponse]:
    """List all registered users. Admin only."""
    service = UserService(db)
    users = service.list_users(current_user)
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Create/Register a new user. Admin only."""
    service = UserService(db)
    try:
        user = service.register_user(payload)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
