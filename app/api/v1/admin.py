from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.lecture import Lecture
from app.models.user import User
from app.models.user_course import UserCourse
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.user import UserCreate, UserOut
from app.services.course_service import create_course
from app.services.user_service import create_user
from app.database.session import get_db
from app.core.email_utils import send_email
from app.core.security import get_current_admin, get_password_hash  # Assuming you have a method to hash passwords
import random
import string
from fastapi import UploadFile, File, Form
from app.schemas.lecture import LectureCreate, LectureOut
from app.services.lecture_service import create_lecture
from app.storage.video_manager import upload_to_storage  # Assuming you have a method to handle video uploads
import uuid
from app.services.lecture_service import get_lectures_by_course

router = APIRouter( tags=["Admin"])

# Helper function to generate a random password
def generate_random_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@router.get("/users", response_model=list[UserOut])
def admin_list_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    List all users as an admin user.
    """
    try:
        users = db.query(User).all()
        
        # For each user, get their course mappings
        for user in users:
            # Use a direct query to get only the columns that exist
            result = db.execute("""
                SELECT id, user_id, course_id, course_name, created_at 
                FROM user_course_mapping 
                WHERE user_id = :user_id
            """, {"user_id": user.id})
            
            # Convert to the expected format
            user.courses = [
                {
                    "id": row[2],  # course_id
                    "name": row[3]  # course_name
                } for row in result
            ]
            
        return users
    except Exception as e:
        print(f"[DEBUG] Error in admin_list_users: {str(e)}")
        raise HTTPException(status_code=400, detail="Error fetching users: " + str(e))

@router.post("/users", response_model=UserOut)
def admin_create_user(user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Create a new user as an admin user.
    """
    try:
        # Store original password for email
        password = user.password
        
        # Create user (password will be hashed in create_user service)
        created_user = create_user(user, db)

        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Send welcome email with credentials
        try:
            send_email(
                to_email=user.email,
                subject="Welcome to Your Financial Astrology Platform",
                body=f"""Dear {user.name},

Welcome to our Financial Astrology platform! Your account has been successfully created.

Your login credentials:
- Email: {user.email}
- Password: {password}

For security reasons, we recommend changing your password after your first login.

If you have any questions, please don't hesitate to contact our support team.

Best regards,
The Financial Astrology Team
"""
            )
        except Exception as email_error:
            print(f"[DEBUG] Error sending welcome email: {str(email_error)}")
            # Don't fail the request if email fails

        return created_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error in admin_create_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Delete a user as an admin user.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting user: " + str(e))

@router.get("/dashboard")
def admin_dashboard(current_admin = Depends(get_current_admin)):
    return {"message": f"Welcome Admin {current_admin.username}"}


'''
Course Management Endpoints

'''
@router.post("/courses/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def admin_create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Create a new course as an admin user.
    """
    try:
        created_course = create_course(db=db, course_data=course)
        return created_course
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating course: " + str(e))
    

@router.get("/courses/", response_model=list[CourseOut])
async def admin_get_courses(db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get all courses as an admin user.
    """
    try:
        courses = db.query(Course).all()
        return courses
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching courses: " + str(e))
    
@router.get("/courses/{course_id}", response_model=CourseOut)
async def admin_get_course(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get a specific course by ID as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching course: " + str(e))
    
@router.put("/courses/{course_id}", response_model=CourseOut)
async def admin_update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Update a specific course by ID as an admin user.
    """
    try:
        existing_course = db.query(Course).filter(Course.id == course_id).first()
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        for key, value in course.dict().items():
            setattr(existing_course, key, value)
        
        db.commit()
        db.refresh(existing_course)
        return existing_course
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating course: " + str(e))
    
@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_course(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Delete a specific course by ID as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        db.delete(course)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting course: " + str(e))
    
'''
User Course Management Endpoints
'''

@router.get("/courses/{course_id}/users", response_model=list[UserOut])
async def admin_get_course_users(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get all users enrolled in a specific course as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        users = db.query(User).join(UserCourse).filter(UserCourse.course_id == course_id).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching course users: " + str(e))
    
@router.post("/courses/{course_id}/assign", response_model=UserOut)
async def admin_assign_course_to_user(course_id: int, user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Assign a course to a user as an admin user.
    Only regular users can be assigned courses, not admins.
    """
    try:
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if user exists and is not an admin
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign courses to admin users"
            )
        
        # Check if user is already enrolled
        existing_enrollment = db.query(UserCourse).filter(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course"
            )
        
        # Create enrollment with course name
        enrollment = UserCourse(
            user_id=user_id,
            course_id=course_id,
            course_name=course.name
        )
        db.add(enrollment)
        db.commit()
        
        # Send email notification
        try:
            send_email(
                to_email=user.email,
                subject="Course Assignment Notification",
                body=f"""Dear {user.name},

You have been assigned to the course: {course.name}

You can now access this course in your dashboard.

Best regards,
The Financial Astrology Team
"""
            )
        except Exception as email_error:
            print(f"[DEBUG] Error sending course assignment email: {str(email_error)}")
            # Don't fail the request if email fails
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error assigning course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.delete("/courses/{course_id}/unassign", status_code=status.HTTP_204_NO_CONTENT)
async def admin_unassign_course_from_user(course_id: int, user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Unassign a course from a user as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the user is enrolled in the course
        enrollment = db.query(UserCourse).filter(UserCourse.user_id == user_id, UserCourse.course_id == course_id).first()
        if not enrollment:
            raise HTTPException(status_code=400, detail="User is not enrolled in this course")
        
        # Delete the enrollment
        db.delete(enrollment)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error unassigning course from user: " + str(e))

'''
Lecture Management Endpoints
'''
@router.post("/courses/{course_id}/lectures", response_model=LectureOut, status_code=status.HTTP_201_CREATED)
async def admin_create_lecture(
    course_id: int, 
    lecture: LectureCreate,
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_admin)
):
    """
    Create a new lecture for a specific course as an admin user.
    Accepts video URL instead of file upload.
    """
    try:
        print(f"[DEBUG] Creating lecture for course {course_id} with data:", lecture.dict())
        
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Create lecture object with video URL
        lecture.course_id = course_id
        created_lecture = create_lecture(db=db, lecture=lecture, course_id=course_id)
        print(f"[DEBUG] Created lecture:", created_lecture)
        return created_lecture
    except HTTPException as he:
        print(f"[ERROR] HTTP Exception in lecture creation:", str(he))
        raise he
    except Exception as e:
        print(f"[ERROR] Failed to create lecture:", str(e))
        raise HTTPException(status_code=400, detail=f"Error creating lecture: {str(e)}")

@router.get("/courses/{course_id}/lectures", response_model=list[LectureOut])
async def admin_get_lectures(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get all lectures for a specific course as an admin user.
    """
    try:
        print(f"[DEBUG] Fetching lectures for course {course_id}")
        
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get lectures using the service function
        lectures = get_lectures_by_course(db=db, course_id=course_id)
        print(f"[DEBUG] Found {len(lectures)} lectures")
        return lectures
    except HTTPException as he:
        print(f"[ERROR] HTTP Exception in lecture fetch:", str(he))
        raise he
    except Exception as e:
        print(f"[ERROR] Failed to fetch lectures:", str(e))
        raise HTTPException(status_code=400, detail=f"Error fetching lectures: {str(e)}")

@router.get("/courses/{course_id}/lectures/{lecture_id}", response_model=LectureOut)
async def admin_get_lecture(course_id: int, lecture_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get a specific lecture by ID for a specific course as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.course_id == course_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        return lecture
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching lecture: " + str(e))
    
@router.put("/courses/{course_id}/lectures/{lecture_id}", response_model=LectureOut)
async def admin_update_lecture(
    course_id: int, 
    lecture_id: int, 
    title: str = Form(...),
    description: str = Form(...),
    order: int = Form(...),
    video: UploadFile = File(None),
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_admin)
):
    """
    Update a specific lecture by ID for a specific course as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.course_id == course_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Update lecture details
        lecture.title = title
        lecture.description = description
        lecture.order = order
        
        # If a new video is uploaded, handle the upload and update the URL
        if video:
            file_extension = video.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            video_url = await upload_to_storage(video, unique_filename)
            lecture.video_url = video_url
        
        db.commit()
        db.refresh(lecture)
        
        return lecture
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating lecture: " + str(e))

@router.delete("/courses/{course_id}/lectures/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_lecture(course_id: int, lecture_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Delete a specific lecture by ID for a specific course as an admin user.
    """
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.course_id == course_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        db.delete(lecture)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting lecture: " + str(e))

@router.get("/lectures/{lecture_id}", response_model=LectureOut)
async def admin_get_lecture_by_id(lecture_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get a specific lecture by ID as an admin user.
    """
    try:
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        return lecture
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching lecture: " + str(e))

@router.put("/lectures/{lecture_id}", response_model=LectureOut)
async def admin_update_lecture_by_id(
    lecture_id: int, 
    title: str = Form(...),
    description: str = Form(...),
    order: int = Form(...),
    video: UploadFile = File(None),
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_admin)
):
    """
    Update a specific lecture by ID as an admin user.
    """
    try:
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Update lecture details
        lecture.title = title
        lecture.description = description
        lecture.order = order
        
        # If a new video is uploaded, handle the upload and update the URL
        if video:
            file_extension = video.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            video_url = await upload_to_storage(video, unique_filename)
            lecture.video_url = video_url
        
        db.commit()
        db.refresh(lecture)
        
        return lecture
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating lecture: " + str(e))

@router.get("/users/{user_id}/courses", response_model=list[CourseOut])
async def admin_get_user_courses(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Get all courses assigned to a specific user as an admin user.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's courses through the relationship
        courses = user.courses
        return courses
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching user courses: " + str(e))

@router.put("/users/{user_id}/toggle-active", response_model=UserOut)
async def admin_toggle_user_active(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    """
    Toggle a user's active status as an admin user.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Toggle the active status
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error toggling user active status: " + str(e))

@router.delete("/users/{user_id}/courses/{course_id}")
async def admin_remove_course_from_user(
    user_id: int, 
    course_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_admin)
):
    """
    Remove a course assignment from a user as an admin.
    """
    try:
        # Check if the mapping exists
        mapping = db.query(UserCourse).filter(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course assignment not found"
            )
        
        # Delete the mapping
        db.delete(mapping)
        db.commit()
        
        return {"message": "Course assignment removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error removing course assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
