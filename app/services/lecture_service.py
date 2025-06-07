from sqlalchemy.orm import Session
from app.models.lecture import Lecture
from app.schemas.lecture import LectureCreate

def create_lecture(db: Session, lecture: LectureCreate, course_id: int) -> Lecture:
    """
    Creates a new lecture linked to a specific course.
    """
    new_lecture = Lecture(
        name=lecture.name,
        thumbnail_url=lecture.thumbnail_url,
        lecture_url=lecture.lecture_url,
        is_active=lecture.is_active,
        course_id=course_id,
        
    )
    db.add(new_lecture)
    db.commit()
    db.refresh(new_lecture)
    return new_lecture
