import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from app.database import get_db
from app.schemas.sensor_reading import SensorReadingCreate, SensorReadingUpdate, SensorReadingInDB
from app.models.sensor_reading import SensorReading
from typing import Optional
from sqlalchemy import select

def convert_to_naive(datetime_obj: Optional[datetime]) -> Optional[datetime]:
    if datetime_obj:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/sensor_readings/", response_model=SensorReadingInDB, status_code=status.HTTP_201_CREATED)
async def create_sensor_reading(sensor_reading: SensorReadingCreate, db: AsyncSession = Depends(get_db)):
    try:
        if sensor_reading.recorded_at:
            sensor_reading.recorded_at = convert_to_naive(sensor_reading.recorded_at)

        new_sensor_reading = await SensorReading.create(db, sensor_reading.dict())
        logger.info(f"New sensor reading created with ID {new_sensor_reading.reading_id}")
        return new_sensor_reading
    except ValueError as e:
        logger.exception(f"ValueError occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error occurred during sensor reading creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/sensor_readings/", response_model=List[SensorReadingInDB])
async def get_all_sensor_readings(db: AsyncSession = Depends(get_db)):
    try:
        sensor_readings = await SensorReading.get_all(db)
        if not sensor_readings:
            raise HTTPException(status_code=404, detail="No sensor readings found")

        for reading in sensor_readings:
            if reading.recorded_at:
                reading.recorded_at = convert_to_naive(reading.recorded_at)

        return sensor_readings
    except Exception as e:
        logger.exception(f"Error occurred while retrieving sensor readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/sensor_readings/{reading_id}", response_model=SensorReadingInDB)
async def update_sensor_reading(reading_id: int, sensor_reading_update: SensorReadingUpdate, db: AsyncSession = Depends(get_db)):
    try:
        if sensor_reading_update.recorded_at:
            sensor_reading_update.recorded_at = convert_to_naive(sensor_reading_update.recorded_at)

        updated_device = await SensorReading.update(db, reading_id, sensor_reading_update.dict(exclude_unset=True))
        if not updated_device:
            raise HTTPException(status_code=404, detail="Sensor reading not found")

        logger.info(f"Sensor reading with ID {reading_id} updated successfully.")
        return updated_device
    except ValueError as e:
        logger.exception(f"ValueError occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error occurred while updating sensor reading: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/sensor_reading/{reading_id}", response_model=SensorReadingInDB)
async def get_sensor_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(SensorReading).where(SensorReading.reading_id == reading_id)
    result = await db.execute(stmt)
    sensor_reading_from_db = result.scalars().first()

    if not sensor_reading_from_db:
        raise HTTPException(status_code=404, detail="Sensor Reading not found")

    return sensor_reading_from_db


@router.get("/sensor_reading/{device_id}", response_model=List[SensorReadingInDB])
async def get_sensor_readings_by_device_id(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        sensor_readings = await SensorReading.get_by_device_id(db, device_id)

        if not sensor_readings:
            logger.warning(f"No sensor readings found for device_id {device_id}")
            raise HTTPException(status_code=404, detail="No sensor readings found for the given device ID")

        logger.info(f"Retrieved {len(sensor_readings)} sensor readings for device_id {device_id}")
        return sensor_readings

    except SQLAlchemyError as db_exc:
        logger.error(f"Database error occurred for device_id {device_id}: {str(db_exc)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception(f"Unexpected error occurred for device_id {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
