from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    role: RoleEnum = RoleEnum.user
    password: str  # Password to be hashed

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str
    role: str
    created_at: datetime
    is_active: bool

    model_config = {
        "from_attributes": True
    }
