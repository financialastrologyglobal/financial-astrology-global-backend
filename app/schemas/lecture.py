from pydantic import BaseModel
from datetime import datetime

class LectureBase(BaseModel):
    name: str
    course_id: int
    thumbnail_url: str = None
    lecture_url: str = None
    is_active: bool = True

class LectureCreate(LectureBase):
    pass

class LectureOut(LectureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
