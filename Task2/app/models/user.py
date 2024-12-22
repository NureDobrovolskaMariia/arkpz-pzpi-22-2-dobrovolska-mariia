from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.database import Base
from enum import Enum
from sqlalchemy.orm import relationship

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(SQLAlchemyEnum(UserRole, native_enum=False), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_incubators = relationship("UserIncubator", back_populates="user")

    @classmethod
    async def check_user_exists(cls, db_session: AsyncSession, email: str):
        stmt = select(cls).where(cls.email == email)
        result = await db_session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def create(cls, db_session: AsyncSession, user_data: dict):
        if 'role' in user_data and isinstance(user_data['role'], str):
            user_data['role'] = UserRole(user_data['role'])
        db_user = cls(**user_data)
        db_session.add(db_user)
        await db_session.commit()
        await db_session.refresh(db_user)
        return db_user

    @classmethod
    async def delete_user(cls, db_session: AsyncSession, user_id: int):
        stmt = select(cls).where(cls.user_id == user_id)
        result = await db_session.execute(stmt)
        db_user = result.scalars().first()
        if db_user:
            await db_session.delete(db_user)
            await db_session.commit()
        return db_user

    @classmethod
    async def get_all_users(cls, db_session: AsyncSession):
        stmt = select(cls)
        result = await db_session.execute(stmt)
        return result.scalars().all()
