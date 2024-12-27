# app/api/sensor_reading.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from app.database import get_db
from app.schemas.sensor_reading import SensorReadingCreate, SensorReadingUpdate, SensorReadingInDB
from app.models.sensor_reading import SensorReading
from app.utils.email import send_email_notification


def convert_to_naive(datetime_obj: Optional[datetime]) -> Optional[datetime]:
    if datetime_obj:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

TEMPERATURE_THRESHOLD = 53.4  


@router.post("/sensor_readings/", response_model=SensorReadingInDB, status_code=status.HTTP_201_CREATED)
async def create_sensor_reading(sensor_reading: SensorReadingCreate, db: AsyncSession = Depends(get_db)):
    try:
        if sensor_reading.recorded_at:
            sensor_reading.recorded_at = convert_to_naive(sensor_reading.recorded_at)

        new_sensor_reading = await SensorReading.create(db, sensor_reading.dict())

        if sensor_reading.value_type == "temperature" and sensor_reading.value > TEMPERATURE_THRESHOLD:
            user_email = "_@gmail.com"  
            subject = "Temperature Alert"
            body = (
                f"Dear User,\n\n"
                f"The temperature value has exceeded the threshold.\n\n"
                f"Details:\n"
                f"Device ID: {sensor_reading.device_id}\n"
                f"Temperature: {sensor_reading.value}°C\n"
                f"Recorded At: {sensor_reading.recorded_at}\n\n"
                f"Please take necessary actions.\n\n"
                f"Best Regards,\n"
                f"Your Monitoring System"
            )
            send_email_notification(user_email, subject, body)

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
        return sensor_readings
    except Exception as e:
        logger.exception(f"Error occurred while retrieving sensor readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/sensor_readings/device/{device_id}", response_model=List[SensorReadingInDB])
async def get_sensor_readings_by_device_id(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        sensor_readings = await SensorReading.get_by_device_id(db, device_id)
        if not sensor_readings:
            raise HTTPException(status_code=404, detail="No sensor readings found for the given device ID")
        return sensor_readings
    except Exception as e:
        logger.exception(f"Error occurred while retrieving sensor readings by device ID {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/sensor_reading/diagnostics/{device_id}", response_model=List[dict])
async def get_sensor_reading_diagnostics(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        sensor_readings = await SensorReading.get_last_four_by_device_id(db, device_id)

        if len(sensor_readings) < 4:
            raise HTTPException(status_code=404, detail="Не вистачає показників для розрахунку диагностики")

        values = [reading.value for reading in sensor_readings]

        mean_value = sum(values) / len(values)

        diagnostics = []
        for reading in sensor_readings:
            error = abs(reading.value - mean_value)
            error_ratio = error / mean_value if mean_value != 0 else 0
            diagnostics.append({
                "reading_id": reading.reading_id,
                "value": reading.value,
                "error": error,
                "error_ratio": error_ratio
            })

        return diagnostics

    except Exception as e:
        logger.exception(f"Помилка при розрахунку диагностики для device_id {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")
