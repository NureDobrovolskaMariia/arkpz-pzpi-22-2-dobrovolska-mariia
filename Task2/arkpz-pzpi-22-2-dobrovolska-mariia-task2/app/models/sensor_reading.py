# app/models/sensor_reading.py
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base
from app.schemas.sensor_reading import SensorReadingInDB
from enum import Enum as Enum
from sqlalchemy import desc
from typing import List

class ValueType(str, Enum):
    temperature = "temperature"
    humidity = "humidity"

class SensorReading(Base):
    __tablename__ = 'sensor_readings'

    reading_id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"), nullable=False)
    value_type = Column(SQLAlchemyEnum(ValueType, native_enum=False), nullable=False)
    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime)

    device = relationship("Device", back_populates="sensor_readings")

    @classmethod
    async def create(cls, db_session: AsyncSession, sensor_readings_data: dict):
        try:
            if 'value_type' in sensor_readings_data and isinstance(sensor_readings_data['value_type'], str):
                sensor_readings_data['value_type'] = ValueType(sensor_readings_data['value_type'])

            sensor_readings = cls(**sensor_readings_data)
            db_session.add(sensor_readings)
            await db_session.commit()
            await db_session.refresh(sensor_readings)
            return sensor_readings
        except Exception as e:
            await db_session.rollback()
            raise e

    @classmethod
    async def get_by_id(cls, db_session: AsyncSession, reading_id: int):
        stmt = select(cls).where(cls.reading_id == reading_id)
        result = await db_session.execute(stmt)
        sensor_reading = result.scalars().first()
        return sensor_reading

    @classmethod
    async def get_by_device_id(cls, db_session: AsyncSession, device_id: int) -> List[SensorReadingInDB]:
        stmt = select(cls).where(cls.device_id == device_id)
        result = await db_session.execute(stmt)
        sensor_readings = result.scalars().all()
        return [SensorReadingInDB.from_orm(reading) for reading in sensor_readings]

    @classmethod
    async def get_all(cls, db_session: AsyncSession):
        stmt = select(cls)
        result = await db_session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, db_session: AsyncSession, reading_id: int, update_data: dict):
        stmt = select(cls).where(cls.reading_id == reading_id)
        result = await db_session.execute(stmt)
        sensor_reading = result.scalars().first()

        if not sensor_reading:
            return None

        for key, value in update_data.items():
            setattr(sensor_reading, key, value)

        await db_session.commit()
        await db_session.refresh(sensor_reading)
        return sensor_reading

    @classmethod
    async def get_last_four_by_device_id(cls, db_session: AsyncSession, device_id: int):
        stmt = select(cls).where(cls.device_id == device_id).order_by(desc(cls.recorded_at)).limit(4)
        result = await db_session.execute(stmt)
        return result.scalars().all()
