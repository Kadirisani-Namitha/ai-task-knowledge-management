import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.models import Task, Document, User, ActivityLog, RoleName

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_analytics(self, user: User) -> dict:
        if user.role.name != RoleName.ADMIN:
            raise PermissionError("Access denied: Admin role required for analytics")

        logger.info("Computing analytics for admin user %d", user.id)

        # ── Totals ────────────────────────────────────────────────────────────
        total_tasks = self._db.scalar(select(func.count(Task.id))) or 0
        total_docs  = self._db.scalar(select(func.count(Document.id))) or 0
        total_users = self._db.scalar(select(func.count(User.id))) or 0
        total_searches = self._db.scalar(
            select(func.count(ActivityLog.id)).where(ActivityLog.action == "SEARCH")
        ) or 0

        # ── Tasks by status ───────────────────────────────────────────────────
        status_rows = self._db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .group_by(Task.status)
        ).all()
        # Return lowercase keys so the frontend bar-chart labels look clean
        tasks_by_status = {
            (row.status.value.lower() if hasattr(row.status, "value") else str(row.status).lower()): row.cnt
            for row in status_rows
        }

        # ── Tasks by assignee (username) ──────────────────────────────────────
        assignee_rows = self._db.execute(
            select(User.username, func.count(Task.id).label("cnt"))
            .join(Task, Task.assigned_to == User.id)
            .group_by(User.username)
            .order_by(func.count(Task.id).desc())
            .limit(10)
        ).all()
        tasks_by_assignee = {row.username: row.cnt for row in assignee_rows}

        # ── Recent activity log (last 20 entries with username) ───────────────
        log_rows = self._db.execute(
            select(
                ActivityLog.id,
                ActivityLog.action,
                ActivityLog.entity_type,
                ActivityLog.entity_id,
                ActivityLog.created_at,
                User.username,
                User.id.label("user_id"),
            )
            .join(User, User.id == ActivityLog.user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(20)
        ).all()
        recent_activity = [
            {
                "id":          row.id,
                "action":      row.action,
                "entity_type": row.entity_type,
                "entity_id":   row.entity_id,
                "created_at":  row.created_at.isoformat() if row.created_at else None,
                "username":    row.username,
                "user_id":     row.user_id,
            }
            for row in log_rows
        ]

        return {
            "total_tasks":       total_tasks,
            "total_documents":   total_docs,
            "total_users":       total_users,
            "total_searches":    total_searches,
            "tasks_by_status":   tasks_by_status,
            "tasks_by_assignee": tasks_by_assignee,
            "recent_activity":   recent_activity,
        }
