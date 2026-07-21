"""
Task CRUD routes with filtering, pagination, and dashboard stats.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskFilter,
)
from app.schemas.common import MessageResponse
from app.services.task_service import TaskService
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/stats",
    summary="Dashboard statistics for the current user",
)
def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return aggregated task counts and completion rate."""
    return TaskService.get_dashboard_stats(db, current_user)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks with filtering and pagination",
)
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    filters = TaskFilter(
        status=status,
        priority=priority,
        search=search,
        due_before=due_before,
        due_after=due_after,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskService.get_all(db, current_user, filters)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return TaskService.create(db, payload, current_user)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve a single task by ID",
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return TaskService.get_by_id(db, task_id, current_user)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update an existing task",
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return TaskService.update(db, task_id, payload, current_user)


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="Soft-delete a task",
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    TaskService.delete(db, task_id, current_user)
    return MessageResponse(message="Task deleted successfully")
