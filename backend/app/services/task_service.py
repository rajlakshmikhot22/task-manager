"""
Task CRUD and business logic service.
"""

import math
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter, TaskListResponse
import logging

logger = logging.getLogger(__name__)

# Map string sort field names to ORM column objects
SORTABLE_FIELDS = {
    "created_at": Task.created_at,
    "updated_at": Task.updated_at,
    "due_date": Task.due_date,
    "priority": Task.priority,
    "status": Task.status,
    "title": Task.title,
}


class TaskService:

    @staticmethod
    def _base_query(db: Session, current_user: User):
        """
        Return the base query scoped to the user.
        Admins can see all tasks; regular users see only their own.
        """
        q = db.query(Task).filter(Task.is_deleted == False)
        if current_user.role != UserRole.ADMIN:
            q = q.filter(Task.owner_id == current_user.id)
        return q

    @staticmethod
    def create(db: Session, payload: TaskCreate, current_user: User) -> Task:
        task = Task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            due_date=payload.due_date,
            owner_id=current_user.id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("Task created: id=%s by user=%s", task.id, current_user.id)
        return task

    @staticmethod
    def get_all(
        db: Session,
        current_user: User,
        filters: TaskFilter,
    ) -> TaskListResponse:
        """
        Return a paginated, filtered, sorted list of tasks.
        """
        q = TaskService._base_query(db, current_user)

        # ── Filtering ─────────────────────────────────────────────────────────
        if filters.status:
            q = q.filter(Task.status == filters.status)
        if filters.priority:
            q = q.filter(Task.priority == filters.priority)
        if filters.due_before:
            q = q.filter(Task.due_date <= filters.due_before)
        if filters.due_after:
            q = q.filter(Task.due_date >= filters.due_after)
        if filters.search:
            term = f"%{filters.search}%"
            q = q.filter(
                or_(Task.title.ilike(term), Task.description.ilike(term))
            )

        total = q.count()

        # ── Sorting ───────────────────────────────────────────────────────────
        sort_col = SORTABLE_FIELDS.get(filters.sort_by, Task.created_at)
        order_fn = desc if filters.sort_order == "desc" else asc
        q = q.order_by(order_fn(sort_col))

        # ── Pagination ────────────────────────────────────────────────────────
        offset = (filters.page - 1) * filters.size
        items = q.offset(offset).limit(filters.size).all()
        pages = math.ceil(total / filters.size) if total else 0

        return TaskListResponse(
            items=items,
            total=total,
            page=filters.page,
            size=filters.size,
            pages=pages,
        )

    @staticmethod
    def get_by_id(db: Session, task_id: int, current_user: User) -> Task:
        q = TaskService._base_query(db, current_user)
        task = q.filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    @staticmethod
    def update(
        db: Session,
        task_id: int,
        payload: TaskUpdate,
        current_user: User,
    ) -> Task:
        task = TaskService.get_by_id(db, task_id, current_user)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Auto-set completed_at when marking a task complete
        if payload.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif payload.status and payload.status != TaskStatus.COMPLETED:
            task.completed_at = None

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        logger.info("Task updated: id=%s by user=%s", task.id, current_user.id)
        return task

    @staticmethod
    def delete(db: Session, task_id: int, current_user: User) -> None:
        task = TaskService.get_by_id(db, task_id, current_user)
        task.is_deleted = True  # soft delete
        db.commit()
        logger.info("Task soft-deleted: id=%s by user=%s", task.id, current_user.id)

    @staticmethod
    def get_dashboard_stats(db: Session, current_user: User) -> dict:
        """
        Return summary statistics for the authenticated user's dashboard.
        Admins get system-wide stats.
        """
        q = db.query(Task).filter(Task.is_deleted == False)
        if current_user.role != UserRole.ADMIN:
            q = q.filter(Task.owner_id == current_user.id)

        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())

        total = q.count()
        todo = q.filter(Task.status == TaskStatus.TODO).count()
        in_progress = q.filter(Task.status == TaskStatus.IN_PROGRESS).count()
        completed = q.filter(Task.status == TaskStatus.COMPLETED).count()
        cancelled = q.filter(Task.status == TaskStatus.CANCELLED).count()
        due_today = q.filter(
            Task.due_date >= today_start,
            Task.due_date <= today_end,
            Task.status != TaskStatus.COMPLETED,
        ).count()
        overdue = q.filter(
            Task.due_date < today_start,
            Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
        ).count()

        # Priority breakdown
        urgent = q.filter(Task.priority == TaskPriority.URGENT).count()
        high = q.filter(Task.priority == TaskPriority.HIGH).count()
        medium = q.filter(Task.priority == TaskPriority.MEDIUM).count()
        low = q.filter(Task.priority == TaskPriority.LOW).count()

        return {
            "total": total,
            "todo": todo,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "due_today": due_today,
            "overdue": overdue,
            "completion_rate": round((completed / total * 100), 1) if total else 0,
            "priority_breakdown": {
                "urgent": urgent,
                "high": high,
                "medium": medium,
                "low": low,
            },
        }
