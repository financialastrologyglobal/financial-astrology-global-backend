from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.course import Course
from app.models.user_course import UserCourse
from app.models.lecture import Lecture
from app.schemas.course import CourseOut
from app.schemas.lecture import LectureOut
from app.database.session import get_db
from app.core.security import get_current_user, TokenData
from app.core.email_utils import send_email
from datetime import datetime
from typing import List

router = APIRouter(tags=["Courses"])

@router.get("/courses", response_model=list[CourseOut])
async def list_courses(db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    """
    List all available courses for the authenticated user.
    """
    try:
        # Get all courses
        courses = db.query(Course).all()
        
        # Get user's enrolled courses
        user_courses = db.query(UserCourse).filter(UserCourse.user_id == current_user.id).all()
        enrolled_course_ids = [uc.course_id for uc in user_courses]
        
        # Filter out enrolled courses
        available_courses = [course for course in courses if course.id not in enrolled_course_ids]
        
        return available_courses
    except Exception as e:
        print(f"[DEBUG] Error listing courses: {str(e)}")
        raise HTTPException(status_code=400, detail="Error fetching courses: " + str(e))

@router.get("/courses/enrolled", response_model=list[CourseOut])
async def list_enrolled_courses(db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    """
    List all courses that the user is enrolled in.
    """
    try:
        # Get user's enrolled courses with course details
        query = text("""
            SELECT c.id, c.name, c.description, c.created_at
            FROM courses c
            INNER JOIN user_course_mapping ucm ON c.id = ucm.course_id
            WHERE ucm.user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": current_user.id})
        
        courses = []
        for row in result:
            # Convert datetime to string if it's not already a string
            created_at = row[3]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            courses.append({
                "id": row[0],
                "name": row[1],
                "description": str(row[2]) if row[2] is not None else "",
                "created_at": created_at
            })
        
        return courses
    except Exception as e:
        print(f"[DEBUG] Error listing enrolled courses: {str(e)}")
        raise HTTPException(status_code=400, detail="Error fetching enrolled courses: " + str(e))

@router.post("/courses/{course_id}/enroll", response_model=CourseOut)
async def enroll_in_course(course_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    """
    Enroll the current user in a course.
    """
    try:
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if user is already enrolled
        existing_enrollment = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already enrolled in this course"
            )
        
        # Create enrollment
        enrollment = UserCourse(
            user_id=current_user.id,
            course_id=course_id,
            course_name=course.name
        )
        db.add(enrollment)
        db.commit()
        
        # Send email notification
        try:
            send_email(
                to_email=current_user.email,
                subject="Course Enrollment Confirmation",
                body=f"""Dear {current_user.username},

You have successfully enrolled in the course: {course.name}

You can now access this course in your dashboard.

Best regards,
The Financial Astrology Team
"""
            )
        except Exception as email_error:
            print(f"[DEBUG] Error sending enrollment email: {str(email_error)}")
            # Don't fail the request if email fails
        
        return course
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error enrolling in course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/courses/{course_id}", response_model=CourseOut)
async def get_course_details(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get details of a specific course.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if user is enrolled
        enrollment = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        ).first()
        
        if not enrollment and current_user.role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You must be enrolled in this course to view its details"
            )
        
        return course
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error getting course details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/courses/{course_id}/lectures", response_model=List[LectureOut])
async def get_course_lectures(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all lectures for a specific course.
    """
    try:
        # First check if user is enrolled in this course
        enrollment = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        ).first()
        
        if not enrollment and current_user.role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You must be enrolled in this course to view its lectures"
            )
        
        # If enrolled, get all lectures for this course
        lectures = db.query(Lecture).filter(Lecture.course_id == course_id).all()
        return lectures
        
    except Exception as e:
        print(f"[DEBUG] Error getting course lectures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/debug/enrollments")
async def debug_enrollments(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Debug endpoint to check user enrollments and lectures.
    """
    try:
        # Get user's enrolled courses
        enrollment_query = text("""
            SELECT c.id, c.name, c.description
            FROM courses c
            INNER JOIN user_course_mapping ucm ON c.id = ucm.course_id
            WHERE ucm.user_id = :user_id
        """)
        
        enrollments = db.execute(enrollment_query, {"user_id": current_user.id})
        
        # Get lectures for each enrolled course
        result = []
        for enrollment in enrollments:
            course_id = enrollment[0]
            lectures_query = text("""
                SELECT l.* 
                FROM lectures l
                WHERE l.course_id = :course_id
            """)
            
            lectures = db.execute(lectures_query, {"course_id": course_id})
            
            result.append({
                "course": {
                    "id": enrollment[0],
                    "name": enrollment[1],
                    "description": enrollment[2]
                },
                "lectures": [
                    {
                        "id": l[0],
                        "name": l[1],
                        "description": l[2],
                        "course_id": l[3],
                        "created_at": l[4],
                        "is_active": l[5],
                        "thumbnail_url": l[6],
                        "lecture_url": l[7]
                    }
                    for l in lectures
                ]
            })
        
        return result
    except Exception as e:
        print(f"[DEBUG] Error in debug endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 