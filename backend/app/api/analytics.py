import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.deps import get_db
from app.models.models import User
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analytics"])


@router.get("/analytics")
def get_analytics(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Get database task and search log analytics. Admin only."""
    service = AnalyticsService(db)
    try:
        return service.get_analytics(current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error fetching analytics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while compiling analytics"
        )
