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
    print(f"[DEBUG] Starting password verification")
    print(f"[DEBUG] Plain password type: {type(plain_password)}")
    print(f"[DEBUG] Plain password length: {len(plain_password)}")
    print(f"[DEBUG] Plain password: {plain_password}")
    print(f"[DEBUG] Hashed password type: {type(hashed_password)}")
    print(f"[DEBUG] Hashed password length: {len(hashed_password)}")
    print(f"[DEBUG] Hashed password: {hashed_password}")
    
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"[DEBUG] Verification result: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Error during password verification: {str(e)}")
        return False

# -----------------------
# JWT Utilities
# -----------------------

class TokenData(BaseModel):
    id: int
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
        user_id = payload.get("id")
        username = payload.get("username")
        email = payload.get("email")
        role = payload.get("role")
        if not (user_id and username and email and role):
            raise ValueError("Missing token fields")
        return TokenData(id=user_id, username=username, email=email, role=role)
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
