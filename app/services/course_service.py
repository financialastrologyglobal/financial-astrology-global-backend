from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course import CourseCreate

def create_course(db: Session, course_data: CourseCreate):
    course = Course(
        name=course_data.name,
        thumbnail_url=course_data.thumbnail_url,
        is_active=course_data.is_active,
        created_at=course_data.created_at or datetime.now(timezone.utc),
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
