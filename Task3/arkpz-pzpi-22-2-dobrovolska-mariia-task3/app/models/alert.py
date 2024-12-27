#app/models/alert.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class Alert(Base):
    __tablename__ = 'alerts'

    alert_id = Column(Integer, primary_key=True, index=True)
    incubator_id = Column(Integer, ForeignKey("incubators.incubator_id"), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

    incubator = relationship("Incubator", back_populates="alerts")
    alert_history = relationship("AlertHistory", back_populates="alert")

    @classmethod
    async def create(cls, session: AsyncSession, alert_data: dict):
        try:
            alert = cls(**alert_data)
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert
        except Exception as e:
            await session.rollback()
            raise e

    @classmethod
    async def get_by_id(cls, session: AsyncSession, alert_id: int):
        result = await session.execute(select(cls).where(cls.alert_id == alert_id))
        return result.scalars().first()

    @classmethod
    async def get_all(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, alert_id: int, update_data: dict):
        result = await session.execute(select(cls).where(cls.alert_id == alert_id))
        alert = result.scalars().first()
        if not alert:
            return None

        for key, value in update_data.items():
            setattr(alert, key, value)

        await session.commit()
        await session.refresh(alert)
        return alert

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, alert_id: int):
        result = await session.execute(select(cls).where(cls.alert_id == alert_id))
        alert = result.scalars().first()
        if not alert:
            return None

        await session.delete(alert)
        await session.commit()
        return alert