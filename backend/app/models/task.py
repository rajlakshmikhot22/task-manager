"""
Task model with priority, status, and soft-delete support.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True
    )
    priority = Column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False, index=True
    )
    due_date = Column(DateTime, nullable=True, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)  # soft delete

    # Foreign Keys
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="tasks")

    # Compound indexes for common query patterns
    __table_args__ = (
        Index("ix_tasks_owner_status", "owner_id", "status"),
        Index("ix_tasks_owner_priority", "owner_id", "priority"),
        Index("ix_tasks_owner_due", "owner_id", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
