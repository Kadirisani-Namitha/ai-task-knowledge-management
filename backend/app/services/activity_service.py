import logging

from sqlalchemy.orm import Session

from app.models.models import ActivityLog
from app.repositories.activity_log_repository import ActivityLogRepository

logger = logging.getLogger(__name__)


class ActivityLogService:
    def __init__(self, db: Session) -> None:
        self._repo = ActivityLogRepository(db)

    def log(
        self,
        user_id: int,
        action: str,
        entity_type: str | None = None,
        entity_id: int | None = None,
        details: dict | None = None,
    ) -> None:
        """
        Write an activity log entry.
        Failures are logged but never bubble up to break the primary operation.
        """
        try:
            entry = ActivityLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            )
            self._repo.create(entry)
        except Exception:
            logger.exception("Failed to write activity log (action=%s, user=%d)", action, user_id)
