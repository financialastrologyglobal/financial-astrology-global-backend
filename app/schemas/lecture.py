from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LectureBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    thumbnail_url: Optional[str] = None
    lecture_url: Optional[str] = None

class LectureCreate(LectureBase):
    course_id: int

class LectureOut(LectureBase):
    id: int
    course_id: int
    created_at: datetime

    class Config:
        from_attributes = True
