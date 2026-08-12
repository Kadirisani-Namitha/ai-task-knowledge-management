import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import SearchResponse
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Search"])


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")


@router.post("/search", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SearchResponse:
    """Perform semantic search over indexed document chunks."""
    service = SearchService(db)
    try:
        return service.search(query=payload.query, user_id=current_user.id, top_k=payload.top_k)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during semantic search")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during search"
        )
