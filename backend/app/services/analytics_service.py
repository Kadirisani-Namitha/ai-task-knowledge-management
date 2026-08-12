import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.models import Task, TaskStatus, ActivityLog, RoleName, User
from app.services.activity_service import ActivityLogService

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_analytics(self, user: User) -> dict:
        # Check permissions: Specs say "Only authorized users should access analytics"
        # Let's ensure only ADMINs (or authorized users) can access it
        if user.role.name != RoleName.ADMIN:
            raise PermissionError("Access denied: Admin role required for analytics")

        logger.info("Computing analytics for admin user %d", user.id)

        # 1. Total tasks count
        total_tasks = self._db.scalar(select(func.count(Task.id))) or 0

        # 2. Completed tasks count
        completed_tasks = self._db.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.COMPLETED)
        ) or 0

        # 3. Pending tasks count
        pending_tasks = self._db.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.PENDING)
        ) or 0

        # 4. Most searched queries from activity_logs
        # JSON field query in MySQL: details->>'$.query'
        # In SQLAlchemy 2.0 we can use the JSON path operator: ActivityLog.details['query'].as_string()
        stmt = (
            select(
                ActivityLog.details["query"].as_string().label("query"),
                func.count(ActivityLog.id).label("count")
            )
            .where(ActivityLog.action == "SEARCH")
            .group_by(ActivityLog.details["query"].as_string())
            .order_by(func.count(ActivityLog.id).desc())
            .limit(10)
        )
        
        raw_searches = self._db.execute(stmt).all()
        most_searched = [
            {"query": row.query, "count": row.count}
            for row in raw_searches if row.query is not None
        ]

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "most_searched_queries": most_searched,
        }
