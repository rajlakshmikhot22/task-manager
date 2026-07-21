"""
Pydantic schemas for Task CRUD and filtering.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title must be 255 characters or fewer")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title must be 255 characters or fewer")
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    size: int
    pages: int


class TaskFilter(BaseModel):
    """Query parameters for filtering/searching tasks."""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    search: Optional[str] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    page: int = 1
    size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"

    @field_validator("size")
    @classmethod
    def limit_page_size(cls, v: int) -> int:
        return min(max(v, 1), 100)

    @field_validator("page")
    @classmethod
    def page_positive(cls, v: int) -> int:
        return max(v, 1)

    @field_validator("sort_by")
    @classmethod
    def valid_sort_field(cls, v: str) -> str:
        allowed = {"created_at", "updated_at", "due_date", "priority", "status", "title"}
        if v not in allowed:
            raise ValueError(f"sort_by must be one of {allowed}")
        return v

    @field_validator("sort_order")
    @classmethod
    def valid_sort_order(cls, v: str) -> str:
        if v.lower() not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower()
