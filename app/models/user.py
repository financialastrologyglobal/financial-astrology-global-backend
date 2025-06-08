from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_class import Base
import enum
from datetime import datetime

# Enum for user roles
class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"
    
    # Other fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20))  # Specify a length for the VARCHAR column (adjust if needed)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationship with courses through UserCourse model
    user_courses = relationship("UserCourse", back_populates="user")
