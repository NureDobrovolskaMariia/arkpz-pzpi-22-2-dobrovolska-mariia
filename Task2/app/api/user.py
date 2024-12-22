from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserLogin
from app.database import get_db
from app.utils.verification import verify_password, hash_password
from typing import List
import logging
from sqlalchemy import select

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/users/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
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


@router.post("/users/login", response_model=UserInDB)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):  # Используем UserLogin
    user_from_db = await User.check_user_exists(db, user.email)
    if not user_from_db or not verify_password(user.password, user_from_db.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user_from_db


@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user_from_db = result.scalars().first()
    if not user_from_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_from_db


@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user_from_db = result.scalars().first()

    if not user_from_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.dict(exclude_unset=True)
    logger.debug(f"User data to update: {user_data}")

    for key, value in user_data.items():
        setattr(user_from_db, key, value)

    try:
        await db.commit()
        await db.refresh(user_from_db)
        logger.info(f"User with ID {user_id} updated successfully.")
    except Exception as e:
        logger.exception(f"Error occurred while updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return user_from_db


@router.get("/users/", response_model=List[UserInDB])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    users = await User.get_all_users(db)
    return users


@router.delete("/users/{user_id}", response_model=UserInDB)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user_from_db = await User.delete_user(db, user_id)
    if not user_from_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_from_db

