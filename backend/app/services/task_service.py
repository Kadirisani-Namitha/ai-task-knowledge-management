import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import Task, TaskStatus, User, RoleName
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.activity_service import ActivityLogService
from app.schemas.schemas import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._task_repo = TaskRepository(db)
        self._user_repo = UserRepository(db)
        self._activity = ActivityLogService(db)

    def create_task(self, payload: TaskCreate, creator_id: int) -> Task:
        # If assigned_to is provided, verify the assignee exists
        if payload.assigned_to is not None:
            assignee = self._user_repo.get_by_id(payload.assigned_to)
            if not assignee:
                raise ValueError("Assignee user does not exist")

        task = Task(
            title=payload.title,
            description=payload.description,
            status=TaskStatus.PENDING,
            assigned_to=payload.assigned_to,
            created_by=creator_id,
        )
        created_task = self._task_repo.create(task)
        logger.info("Task %d created by user %d", created_task.id, creator_id)
        return created_task

    def update_task(self, task_id: int, payload: TaskUpdate, user: User) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if not task:
            raise KeyError("Task not found")

        is_admin = user.role.name == RoleName.ADMIN

        # Ownership protection: Regular users can only access their assigned tasks
        if not is_admin and task.assigned_to != user.id:
            raise PermissionError("Access denied: You are not assigned to this task")

        # Authorization: Regular users can only update status to COMPLETED/PENDING
        if not is_admin:
            if payload.title is not None or payload.description is not None or payload.assigned_to is not None:
                raise PermissionError("Access denied: Only administrators can modify task fields other than status")

        # Apply updates
        original_status = task.status

        if payload.title is not None:
            task.title = payload.title
        if payload.description is not None:
            task.description = payload.description
        if payload.assigned_to is not None:
            # Verify assignee exists
            assignee = self._user_repo.get_by_id(payload.assigned_to)
            if not assignee:
                raise ValueError("Assignee user does not exist")
            task.assigned_to = payload.assigned_to

        if payload.status is not None:
            # Validate status (case-insensitive)
            try:
                new_status = TaskStatus(payload.status.upper())
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid status value: {payload.status}")

            task.status = new_status
            if new_status == TaskStatus.COMPLETED and original_status != TaskStatus.COMPLETED:
                task.completed_at = datetime.now(timezone.utc)
            elif new_status == TaskStatus.PENDING:
                task.completed_at = None

        updated_task = self._task_repo.update(task)

        # Log activity
        self._activity.log(
            user_id=user.id,
            action="TASK_UPDATE",
            entity_type="task",
            entity_id=updated_task.id,
            details={
                "status_changed": original_status != updated_task.status,
                "new_status": updated_task.status.value if isinstance(updated_task.status, TaskStatus) else updated_task.status,
            },
        )

        logger.info("Task %d updated by user %d", updated_task.id, user.id)
        return updated_task

    def get_task(self, task_id: int, user: User) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if not task:
            raise KeyError("Task not found")

        is_admin = user.role.name == RoleName.ADMIN
        if not is_admin and task.assigned_to != user.id:
            raise PermissionError("Access denied: You are not assigned to this task")

        return task

    def list_tasks(
        self,
        user: User,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Task]:
        is_admin = user.role.name == RoleName.ADMIN

        # Filter by status if provided
        task_status = None
        if status is not None:
            try:
                # Frontend sends lowercase ('pending'/'completed') — normalise to uppercase
                task_status = TaskStatus(status.upper())
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid status filter: {status}")

        if is_admin:
            # Admins can list all tasks
            return self._task_repo.list_tasks(skip=skip, limit=limit, status=task_status)
        else:
            # Users can only list tasks assigned to them
            return self._task_repo.list_tasks(
                skip=skip,
                limit=limit,
                assigned_to=user.id,
                status=task_status,
            )

    def delete_task(self, task_id: int, user: User) -> None:
        # Only admins can delete tasks
        if user.role.name != RoleName.ADMIN:
            raise PermissionError("Access denied: Only administrators can delete tasks")

        task = self._task_repo.get_by_id(task_id)
        if not task:
            raise KeyError("Task not found")

        self._task_repo.delete(task)
        logger.info("Task %d deleted by admin %d", task_id, user.id)
