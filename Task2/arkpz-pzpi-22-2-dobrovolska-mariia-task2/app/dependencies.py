from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.utils.auth import verify_access_token
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_access_token(token)
        user = payload.get("sub")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

def is_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

def is_user(user: dict = Depends(get_current_user)):
    if user.get("role") not in [UserRole.admin.value, UserRole.user.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user
