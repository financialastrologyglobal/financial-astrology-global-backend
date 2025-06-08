from app.models.user import User
from app.models.course import Course
from app.models.lecture import Lecture
from app.models.user_course import UserCourse

# This ensures all models are imported and registered with SQLAlchemy
__all__ = ['User', 'Course', 'Lecture', 'UserCourse']
