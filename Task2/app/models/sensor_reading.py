from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as Enum
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.sensor_reading import SensorReadingInDB
from typing import List

class ValueType(str, Enum):
    temperature = "temperature"
    humidity = "humidity"

class SensorReading(Base):
    __tablename__ = 'sensor_readings'

    reading_id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"), nullable=False)
    value_type = Column(SQLAlchemyEnum(ValueType, native_enum=False), nullable=False)  # Enum definition with a name

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
        result = await db_session.execute(
            cls.__table__.select().where(cls.reading_id == reading_id)
        )
        sensor_readings = result.scalar()
        if sensor_readings:
            return SensorReadingInDB.from_orm(sensor_readings)
        return None

    @classmethod
    async def get_by_device_id(cls, db_session: AsyncSession, device_id: int) -> List[SensorReadingInDB]:
        result = await db_session.execute(
            select(cls).where(cls.device_id == device_id)
        )
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
        sensor_readings = result.scalars().first()

        if not sensor_readings:
            return None

        for key, value in update_data.items():
            setattr(sensor_readings, key, value)

        if sensor_readings.value_type not in ['temperature', 'humidity']:
            raise ValueError('value_type must be either "temperature" or "humidity"')

        await db_session.commit()
        await db_session.refresh(sensor_readings)
        return sensor_readings

