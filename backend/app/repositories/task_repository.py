from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, task_id: int) -> Task | None:
        return self._db.get(Task, task_id)

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 50,
        assigned_to: int | None = None,
        created_by: int | None = None,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        stmt = select(Task)
        if assigned_to is not None:
            stmt = stmt.where(Task.assigned_to == assigned_to)
        if created_by is not None:
            stmt = stmt.where(Task.created_by == created_by)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        stmt = stmt.offset(skip).limit(limit)
        return list(self._db.scalars(stmt).all())

    def create(self, task: Task) -> Task:
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self._db.commit()
        self._db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self._db.delete(task)
        self._db.commit()
