from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CourseCreate(BaseModel):
    name: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class CourseOut(BaseModel):
    id: int
    name: str
    thumbnail_url: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
