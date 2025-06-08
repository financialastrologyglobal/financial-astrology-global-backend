from sqlalchemy.orm import Session
from app.models.lecture import Lecture
from app.schemas.lecture import LectureCreate
from fastapi import HTTPException

def create_lecture(db: Session, lecture: LectureCreate, course_id: int) -> Lecture:
    """
    Creates a new lecture linked to a specific course.
    """
    try:
        print(f"[DEBUG] Creating lecture with data: {lecture.dict()}")
        
        # Validate required fields
        if not lecture.name:
            raise HTTPException(status_code=400, detail="Lecture name is required")
        if not lecture.description:
            raise HTTPException(status_code=400, detail="Lecture description is required")
        if not lecture.lecture_url:
            raise HTTPException(status_code=400, detail="Lecture URL is required")
            
        # Create lecture object with video URL
        new_lecture = Lecture(
            name=lecture.name,
            description=lecture.description,
            thumbnail_url=lecture.thumbnail_url,
            lecture_url=lecture.lecture_url,
            is_active=lecture.is_active,
            course_id=course_id,  # Use the course_id from the URL parameter
        )
        
        print(f"[DEBUG] Created lecture object: {new_lecture.__dict__}")
        
        db.add(new_lecture)
        db.commit()
        db.refresh(new_lecture)
        
        print(f"[DEBUG] Saved lecture to database: {new_lecture.__dict__}")
        
        return new_lecture
    except Exception as e:
        print(f"[ERROR] Failed to create lecture: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating lecture: {str(e)}")

def get_lectures_by_course(db: Session, course_id: int) -> list[Lecture]:
    """
    Get all lectures for a specific course.
    """
    try:
        return db.query(Lecture).filter(Lecture.course_id == course_id).all()
    except Exception as e:
        print(f"[ERROR] Failed to fetch lectures: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching lectures: {str(e)}")
