from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, get_password_hash

def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """Authenticate a user by email and password"""
    print(f"[DEBUG] authenticate_user called with email: {email}")
    
    # Get user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"[DEBUG] No user found with email: {email}")
        return None

    print(f"[DEBUG] Found user: {user.email}")
    print(f"[DEBUG] User role: {user.role}")
    print(f"[DEBUG] User password hash length: {len(user.password)}")
    
    # Verify password
    if not verify_password(password, user.password):
        print(f"[DEBUG] Password verification failed for user: {user.email}")
        return None

    print(f"[DEBUG] Password verified successfully for user: {user.email}")
    return user

def change_password(user: User, new_password: str, db: Session) -> bool:
    """Change a user's password"""
    try:
        user.password = get_password_hash(new_password)
        db.commit()
        return True
    except Exception as e:
        print(f"[DEBUG] Error changing password: {str(e)}")
        db.rollback()
        return False