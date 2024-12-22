import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from app.database import get_db
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceInDB
from app.models.device import Device
from typing import Optional
from sqlalchemy import select

def convert_to_naive(datetime_obj: Optional[datetime]) -> Optional[datetime]:
    if datetime_obj:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/devices/", response_model=DeviceInDB, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, db: AsyncSession = Depends(get_db)):
    try:
        if device.last_reported_at:
            device.last_reported_at = convert_to_naive(device.last_reported_at)

        new_device = await Device.create(db, device.dict())
        logger.info(f"New device created with ID {new_device.device_id}")
        return new_device
    except Exception as e:
        logger.exception(f"Error occurred during device creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/devices/{device_id}", response_model=DeviceInDB)
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Device).where(Device.device_id == device_id)
    result = await db.execute(stmt)
    device_from_db = result.scalars().first()

    if not device_from_db:
        raise HTTPException(status_code=404, detail="Device not found")

    return device_from_db



@router.put("/devices/{device_id}", response_model=DeviceInDB)
async def update_device(device_id: int, device_update: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    try:
        if device_update.last_reported_at:
            device_update.last_reported_at = convert_to_naive(device_update.last_reported_at)

        updated_device = await Device.update(db, device_id, device_update.dict(exclude_unset=True))
        if not updated_device:
            raise HTTPException(status_code=404, detail="Device not found")

        logger.info(f"Device with ID {device_id} updated successfully.")
        return updated_device
    except Exception as e:
        logger.exception(f"Error occurred while updating device: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/devices/", response_model=List[DeviceInDB])
async def get_all_devices(db: AsyncSession = Depends(get_db)):
    try:
        devices = await Device.get_all(db)
        if not devices:
            raise HTTPException(status_code=404, detail="No devices found")

        for device in devices:
            if device.last_reported_at:
                device.last_reported_at = convert_to_naive(device.last_reported_at)

        return devices
    except Exception as e:
        logger.exception(f"Error occurred while retrieving devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/devices/{device_id}", response_model=dict)
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted_device = await Device.delete_by_id(db, device_id)
        if not deleted_device:
            raise HTTPException(status_code=404, detail="Device not found")
        return {"message": "Device deleted successfully", "device_id": device_id}
    except SQLAlchemyError as e:
        logger.exception(f"SQL error during deletion of device ID {device_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Error occurred during deletion.")
    except Exception as e:
        logger.exception(f"Error occurred while deleting device: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
