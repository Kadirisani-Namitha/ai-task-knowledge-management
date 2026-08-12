from sqlalchemy.orm import Session

from app.models.models import ActivityLog


class ActivityLogRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, log: ActivityLog) -> ActivityLog:
        self._db.add(log)
        self._db.commit()
        self._db.refresh(log)
        return log
