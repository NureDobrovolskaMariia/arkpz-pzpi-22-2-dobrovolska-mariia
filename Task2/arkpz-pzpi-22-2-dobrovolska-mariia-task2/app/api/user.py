from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserLogin
from app.database import get_db
from app.utils.verification import verify_password, hash_password
from typing import List
import logging
from sqlalchemy import select
from app.dependencies import is_admin, is_user
from app.utils.auth import create_access_token
from app.dependencies import get_current_user
from datetime import datetime


user_router = APIRouter()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@user_router.post("/users/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await User.check_user_exists(db, user.email)
        if existing_user:
            logger.error(f"User with email {user.email} already exists.")
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = hash_password(user.password)
        user_data = user.dict()
        user_data["password"] = hashed_password

        new_user = await User.create(db, user_data)
        logger.info(f"New user created with ID {new_user.user_id}")
        return new_user
    except Exception as e:
        logger.exception(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@user_router.post("/users/login", response_model=str)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    user_from_db = await User.check_user_exists(db, user.email)
    if not user_from_db or not verify_password(user.password, user_from_db.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user_from_db.is_blocked:
        if user_from_db.blocked_until and user_from_db.blocked_until > datetime.utcnow():
            raise HTTPException(status_code=403, detail="You are temporarily blocked")
        else:
            user_from_db.is_blocked = False
            user_from_db.blocked_until = None
            await db.commit()

    token = create_access_token({"sub": user_from_db.email, "role": user_from_db.role.value})
    return token


@user_router.get("/users/{user_id}", response_model=UserInDB, dependencies=[Depends(get_current_user)])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.put("/users/{user_id}", response_model=UserInDB, dependencies=[Depends(get_current_user)])
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    updated_user = await User.update(db, user_id, update_data)
    return updated_user


@user_router.get("/users/", response_model=List[UserInDB], dependencies=[Depends(is_admin)])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    users = await User.get_all_users(db)
    return users


@user_router.delete("/users/{user_id}", response_model=UserInDB, dependencies=[Depends(is_admin)])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await User.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/users/{user_id}/block")
async def block_user(user_id: int, block_minutes: int, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Blocking user with ID {user_id} for {block_minutes} minutes")

        user = await User.block_user(db, user_id, block_minutes)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": f"User {user.email} is blocked for {block_minutes} minutes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@user_router.post("/users/{user_id}/unblock")
async def unblock_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:

        print(f"Unblocking user with ID {user_id}")

        user = await User.unblock_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": f"User {user.email} is unblocked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@user_router.post("/users/logout", status_code=status.HTTP_200_OK)
async def logout(response: JSONResponse):

    try:
        response.delete_cookie(key="access_token")

        return {"message": "Successfully logged out"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while logging out: {str(e)}")