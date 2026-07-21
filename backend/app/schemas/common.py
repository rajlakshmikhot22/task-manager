"""
Shared/reusable Pydantic schemas.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

DataT = TypeVar("DataT")


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel, Generic[DataT]):
    items: List[DataT]
    total: int
    page: int
    size: int
    pages: int
