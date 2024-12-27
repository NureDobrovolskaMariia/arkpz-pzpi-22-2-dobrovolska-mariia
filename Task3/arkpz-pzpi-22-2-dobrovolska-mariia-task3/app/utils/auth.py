from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import UserRole
from typing import Optional

SECRET_KEY = "z8J&9q@F4L#v5nW!XyRdPbM$3T@u7G^Kz*jf8QwLmV2xHZp#%sYr6gXnTz4cR&b"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    return payload

def role_required(required_role: UserRole):
    def role_dependency(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return role_dependency
