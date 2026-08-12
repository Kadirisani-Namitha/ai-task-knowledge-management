import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Create a new task. Admin only."""
    service = TaskService(db)
    try:
        task = service.create_task(payload, current_user.id)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status: str | None = None,
) -> list[TaskResponse]:
    """List tasks. Admin sees all; User sees assigned tasks. Optional status filter."""
    service = TaskService(db)
    try:
        tasks = service.list_tasks(user=current_user, status=status)
        return [TaskResponse.model_validate(t) for t in tasks]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Get task by ID with ownership check."""
    service = TaskService(db)
    try:
        task = service.get_task(task_id, current_user)
        return TaskResponse.model_validate(task)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Update task fields. User can only update status if assigned. Admin can update everything."""
    service = TaskService(db)
    try:
        task = service.update_task(task_id, payload, current_user)
        return TaskResponse.model_validate(task)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except (ValueError, PermissionError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if isinstance(e, PermissionError) else status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a task. Admin only."""
    service = TaskService(db)
    try:
        service.delete_task(task_id, current_user)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
