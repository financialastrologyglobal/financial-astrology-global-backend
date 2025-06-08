from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from app.utils.url_utils import normalize_url

class LectureBase(BaseModel):
    name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    lecture_url: str  # Made required
    is_active: bool = True
    
    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        if v is not None:
            return normalize_url(v)
        return v
        
    @validator('lecture_url')
    def validate_lecture_url(cls, v):
        if v:
            return normalize_url(v)
        return v

class LectureCreate(LectureBase):
    course_id: int

class LectureOut(LectureBase):
    id: int
    course_id: int
    created_at: datetime

    class Config:
        from_attributes = True
