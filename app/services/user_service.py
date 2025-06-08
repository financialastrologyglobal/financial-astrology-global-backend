from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from sqlalchemy.exc import SQLAlchemyError

def create_user(user_data: UserCreate, db: Session) -> User | None:
    """Create a new user with a hashed password"""
    print(f"[DEBUG] Creating user with email: {user_data.email}")
    
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        print(f"[DEBUG] User with email {user_data.email} already exists")
        return None
    
    try:
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        print(f"[DEBUG] Password hashed successfully")

        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            role=user_data.role,
            password=hashed_password,
        )

        print(f"[DEBUG] Attempting to add user to database")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"[DEBUG] User created successfully: {new_user.email}")
        return new_user
    except SQLAlchemyError as e:
        print(f"[DEBUG] Database error creating user: {str(e)}")
        db.rollback()
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        print(f"[DEBUG] Unexpected error creating user: {str(e)}")
        db.rollback()
        raise Exception(f"Unexpected error: {str(e)}")
