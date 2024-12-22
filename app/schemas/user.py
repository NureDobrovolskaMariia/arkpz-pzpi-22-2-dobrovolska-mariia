from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
import re

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'user']:
            raise ValueError('Role must be either "admin" or "user"')
        return v

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

    @validator('role')
    def validate_role(cls, v):
        if v and v not in ['admin', 'user']:
            raise ValueError('Role must be either "admin" or "user"')
        return v

class UserInDB(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

