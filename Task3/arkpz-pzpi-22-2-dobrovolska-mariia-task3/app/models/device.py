#app/models/device.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import Base
from datetime import datetime
from app.schemas.device import DeviceInDB

class Device(Base):
    __tablename__ = 'devices'

    device_id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String, nullable=False)
    incubator_id = Column(Integer, ForeignKey("incubators.incubator_id"), nullable=False)
    last_reported_at = Column(DateTime)

    incubator = relationship("Incubator", back_populates="devices")
    sensor_readings = relationship("SensorReading", back_populates="device")

    @classmethod
    async def create(cls, db_session: AsyncSession, device_data: dict):
        try:
            device = cls(**device_data)
            db_session.add(device)
            await db_session.commit()
            await db_session.refresh(device)
            return device
        except Exception as e:
            await db_session.rollback()
            raise e

    @classmethod
    async def get_by_id(cls, db_session: AsyncSession, device_id: int):
        result = await db_session.execute(
            cls.__table__.select().where(cls.device_id == device_id)
        )
        device = result.scalar()
        if device:
            return DeviceInDB.from_orm(device)
        return None

    @classmethod
    async def get_all(cls, db_session: AsyncSession):
        stmt = select(cls)
        result = await db_session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, db_session: AsyncSession, device_id: int, update_data: dict):
        stmt = select(cls).where(cls.device_id == device_id)
        result = await db_session.execute(stmt)
        device = result.scalars().first()

        if not device:
            return None

        for key, value in update_data.items():
            setattr(device, key, value)

        if 'last_reported_at' not in update_data:
            device.last_reported_at = datetime.utcnow()

        await db_session.commit()
        await db_session.refresh(device)
        return device

    @classmethod
    async def delete_by_id(cls, db_session: AsyncSession, device_id: int):
        try:
            stmt = select(cls).where(cls.device_id == device_id)
            result = await db_session.execute(stmt)
            device = result.scalars().first()

            if not device:
                return None

            await db_session.delete(device)
            await db_session.commit()
            return device
        except Exception as e:
            await db_session.rollback()
            raise e

