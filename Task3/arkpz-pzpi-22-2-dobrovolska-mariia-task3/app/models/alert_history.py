#app/models/alert_history.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class AlertHistory(Base):
    __tablename__ = 'alert_history'

    history_id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.alert_id"), nullable=False)
    status = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)

    alert = relationship("Alert", back_populates="alert_history")

    @classmethod
    async def create(cls, db_session: AsyncSession, alert_history_data: dict):
        try:
            alert_history = cls(**alert_history_data)
            db_session.add(alert_history)
            await db_session.commit()
            await db_session.refresh(alert_history)
            return alert_history
        except Exception as e:
            await db_session.rollback()
            raise e

    @classmethod
    async def get_all(cls, db_session: AsyncSession):
        stmt = select(cls)
        result = await db_session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db_session: AsyncSession, history_id: int):
        stmt = select(cls).where(cls.history_id == history_id)
        result = await db_session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def update(cls, db_session: AsyncSession, history_id: int, update_data: dict):
        try:
            stmt = select(cls).where(cls.history_id == history_id)
            result = await db_session.execute(stmt)
            alert_history = result.scalars().first()

            if not alert_history:
                return None

            allowed_keys = {"status", "changed_at"}
            for key, value in update_data.items():
                if key in allowed_keys:
                    setattr(alert_history, key, value)

            await db_session.commit()
            await db_session.refresh(alert_history)
            return alert_history
        except Exception as e:
            await db_session.rollback()
            raise e

