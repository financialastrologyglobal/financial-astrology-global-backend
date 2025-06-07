from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session

def create_user(user_data: UserCreate, db: Session) -> User | None:
    if db.query(User).filter(User.email == user_data.email).first():
        return None
    print(user_data.password)

    # Create new user with hashed password
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        role=user_data.role,
        password=user_data.password,  # Store the hashed password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
