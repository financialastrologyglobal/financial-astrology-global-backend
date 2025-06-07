from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from app.database.session import Base

class UserCourse(Base):
    __tablename__ = "user_course_mapping"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
