#app/api/alert_history.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert_history import AlertHistory
from app.schemas.alert_history import AlertHistoryCreate, AlertHistoryUpdate, AlertHistoryInDB
from typing import Optional, List
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
import logging

def convert_to_naive(datetime_obj: Optional[datetime]) -> Optional[datetime]:
    if datetime_obj:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/alert_history/", response_model=AlertHistoryInDB, status_code=status.HTTP_201_CREATED)
async def create_alert_history(alert_history: AlertHistoryCreate, db: AsyncSession = Depends(get_db)):
    try:
        if alert_history.changed_at:
            alert_history.changed_at = convert_to_naive(alert_history.changed_at)

        new_alert_history = await AlertHistory.create(db, alert_history.dict())
        logger.info(f"New alert history created with ID {new_alert_history.history_id}")
        return new_alert_history
    except Exception as e:
        logger.exception(f"Error occurred during alert history creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/alert_history/{history_id}", response_model=AlertHistoryInDB)
async def get_alert_history_by_id(history_id: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(AlertHistory).where(AlertHistory.history_id == history_id)
        result = await db.execute(stmt)
        alert_history_from_db = result.scalars().first()

        if not alert_history_from_db:
            raise HTTPException(status_code=404, detail="Alert history record not found")

        return alert_history_from_db
    except Exception as e:
        logger.exception(f"Error occurred while retrieving alert history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/alert_history/{history_id}", response_model=AlertHistoryInDB)
async def update_alert_history(history_id: int, alert_history_update: AlertHistoryUpdate, db: AsyncSession = Depends(get_db)):
    try:
        if alert_history_update.changed_at:
            alert_history_update.changed_at = convert_to_naive(alert_history_update.changed_at)

        updated_alert_history = await AlertHistory.update(
            db, history_id, alert_history_update.dict(exclude_unset=True)
        )

        if not updated_alert_history:
            logger.error(f"Alert history record with ID {history_id} not found.")
            raise HTTPException(status_code=404, detail="Alert history record not found")

        logger.info(f"Alert history record with ID {history_id} updated successfully.")
        return updated_alert_history
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error occurred while updating alert history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/alert_history/", response_model=List[AlertHistoryInDB])
async def get_all_alert_history(db: AsyncSession = Depends(get_db)):
    try:
        alert_history_records = await AlertHistory.get_all(db)
        if not alert_history_records:
            raise HTTPException(status_code=404, detail="No alert history records found")

        for record in alert_history_records:
            if record.changed_at:
                record.changed_at = convert_to_naive(record.changed_at)

        return alert_history_records
    except Exception as e:
        logger.exception(f"Error occurred while retrieving alert history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
