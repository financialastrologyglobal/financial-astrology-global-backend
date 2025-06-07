from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# -----------------------
# Password Utilities
# -----------------------

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    print(f"Verifying password: {plain_password} against {hashed_password}")
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------
# JWT Utilities
# -----------------------

class TokenData(BaseModel):
    username: str
    email: str
    role: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=3)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("username")
        email = payload.get("email")
        role = payload.get("role")
        if not (username and email and role):
            raise ValueError("Missing token fields")
        return TokenData(username=username, email=email, role=role)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# -----------------------
# Dependencies
# -----------------------

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return decode_token(token)

def get_current_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user
