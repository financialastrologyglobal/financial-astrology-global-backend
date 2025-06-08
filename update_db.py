from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Create the database engine
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)

# Create a base class for declarative models
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Define the models
class UserCourse(Base):
    __tablename__ = "user_courses"
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    courses = relationship("Course", secondary="user_courses", back_populates="users")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    thumbnail_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    users = relationship("User", secondary="user_courses", back_populates="courses")
    lectures = relationship("Lecture", back_populates="course")

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    thumbnail_url = Column(String(255))
    lecture_url = Column(String(255))
    course = relationship("Course", back_populates="lectures")

def update_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database schema updated successfully!")

if __name__ == "__main__":
    update_database() 