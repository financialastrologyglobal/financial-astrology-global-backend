from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash
import os

def create_initial_admin(db: Session):
    """Create initial admin user if no admin exists"""
    # Check if admin already exists
    admin = db.query(User).filter(User.role == RoleEnum.admin).first()
    if not admin:
        # Create admin user with environment variables or default credentials
        admin_email = os.getenv("ADMIN_EMAIL", "admin@finanastrology.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this in production
        
        admin_user = User(
            name="Admin",
            email=admin_email,
            phone_number="0000000000",
            role=RoleEnum.admin,
            password=get_password_hash(admin_password),
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Initial admin user created with email: {admin_email}")
    else:
        print("Admin user already exists")
