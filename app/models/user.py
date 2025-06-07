from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database.session import Base
import enum
from datetime import datetime as DateTime1

# Enum for user roles
class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"
    
    # Other fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Specify a length for the VARCHAR column
    email = Column(String(255), unique=True, index=True)  # Specify a length for the VARCHAR column
    phone_number = Column(String(20))  # Specify a length for the VARCHAR column (adjust if needed)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    password = Column(String(255))  # Specify a length for the VARCHAR column
    created_at = Column(DateTime, default=DateTime1.now)
    is_active = Column(Boolean, default=True)

    # Relationships if any
    # courses = relationship("Course", back_populates="owner")
