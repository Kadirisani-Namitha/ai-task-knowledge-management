import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.deps import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    repo = UserRepository(db)
    user = repo.get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        # Intentionally vague error to avoid leaking whether the username exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    token = create_access_token(subject=user.id)
    logger.info("User %s logged in", user.id)
    return TokenResponse(access_token=token)
