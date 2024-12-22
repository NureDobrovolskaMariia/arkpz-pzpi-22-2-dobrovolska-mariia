from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date
from app.schemas.incubator import IncubatorInDB
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_incubator import UserIncubator
from app.models.device import Device
from app.models.alert import Alert
from sqlalchemy import update
from sqlalchemy import delete

class Incubator(Base):
    __tablename__ = 'incubators'

    incubator_id = Column(Integer, primary_key=True, index=True)
    incubator_name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    filled_at = Column(Date, nullable=True)
    target_temperature = Column(Float, nullable=False)
    target_humidity = Column(Float, nullable=False)

    user_incubators = relationship("UserIncubator", back_populates="incubator")
    devices = relationship("Device", back_populates="incubator")
    alerts = relationship("Alert", back_populates="incubator")

    @classmethod
    async def create(cls, db_session, data: dict):
        if "filled_at" in data and isinstance(data["filled_at"], str):
            data["filled_at"] = date.fromisoformat(data["filled_at"])

        incubator = cls(**data)
        db_session.add(incubator)
        await db_session.commit()
        await db_session.refresh(incubator)
        return incubator

    @classmethod
    async def get_all(cls, db_session):
        result = await db_session.execute(cls.__table__.select())
        incubators = result.fetchall()
        return [IncubatorInDB.from_orm(incubator) for incubator in incubators]

    @classmethod
    async def get_by_id(cls, db_session, incubator_id: int):
        result = await db_session.execute(
            cls.__table__.select().where(cls.incubator_id == incubator_id)
        )
        incubator = result.scalar()
        if incubator:
            return IncubatorInDB.from_orm(incubator)
        return None

    @classmethod
    async def update(cls, db_session, incubator_id: int, data: dict):
        result = await db_session.execute(
            cls.__table__.update().where(cls.incubator_id == incubator_id).values(**data).returning(cls.__table__)
        )
        await db_session.commit()
        updated_incubator = result.scalars().first()
        if updated_incubator:
            return IncubatorInDB.from_orm(updated_incubator)
        return None

    @classmethod
    async def delete_by_id(cls, db_session: AsyncSession, incubator_id: int):
        try:
            await db_session.execute(
                delete(UserIncubator).where(UserIncubator.incubator_id == incubator_id)
            )

            await db_session.execute(
                update(Device).where(Device.incubator_id == incubator_id).values(incubator_id=None)
            )

            await db_session.execute(
                update(Alert).where(Alert.incubator_id == incubator_id).values(incubator_id=None)
            )

            stmt = select(cls).where(cls.incubator_id == incubator_id)
            result = await db_session.execute(stmt)
            incubator = result.scalars().first()

            if incubator:
                await db_session.delete(incubator)
                await db_session.commit()
                return incubator

            return None

        except Exception as e:
            await db_session.rollback()
            raise e