from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course import CourseCreate

def create_course(db: Session, course_data: CourseCreate):
    try:
        print(f"[DEBUG] Creating course with data: {course_data.dict()}")
        
        course = Course(
            name=course_data.name,
            description=course_data.description,
            thumbnail_url=course_data.thumbnail_url,
            is_active=course_data.is_active,
            created_at=course_data.created_at or datetime.now(timezone.utc),
        )
        
        db.add(course)
        db.commit()
        db.refresh(course)
        
        print(f"[DEBUG] Course created successfully: {course.id}")
        return course
    except Exception as e:
        print(f"[DEBUG] Error creating course: {str(e)}")
        db.rollback()
        raise
