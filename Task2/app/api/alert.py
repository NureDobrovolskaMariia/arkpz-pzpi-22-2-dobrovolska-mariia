import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from app.database import get_db
from app.schemas.alert import AlertCreate, AlertUpdate, AlertInDB
from app.models.alert import Alert
from typing import Optional

def convert_to_naive(datetime_obj: Optional[datetime]) -> Optional[datetime]:
    if datetime_obj:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/alerts/", response_model=AlertInDB, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_alert = await Alert.create(db, alert.dict())
        logger.info(f"New alert created with ID {new_alert.alert_id}")
        return new_alert
    except Exception as e:
        logger.exception(f"Error occurred during alert creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/alerts/{alert_id}", response_model=AlertInDB)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await Alert.get_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.created_at:
        alert.created_at = convert_to_naive(alert.created_at)
    return alert

@router.put("/alerts/{alert_id}", response_model=AlertInDB)
async def update_alert(alert_id: int, alert_update: AlertUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated_alert = await Alert.update(db, alert_id, alert_update.dict(exclude_unset=True))
        if not updated_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        logger.info(f"Alert with ID {alert_id} updated successfully.")
        return updated_alert
    except Exception as e:
        logger.exception(f"Error occurred while updating alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/alerts/", response_model=List[AlertInDB])
async def get_all_alerts(db: AsyncSession = Depends(get_db)):
    try:
        alerts = await Alert.get_all(db)
        if not alerts:
            raise HTTPException(status_code=404, detail="No alerts found")
        for alert in alerts:
            if alert.created_at:
                alert.created_at = convert_to_naive(alert.created_at)
        return alerts
    except Exception as e:
        logger.exception(f"Error occurred while retrieving alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/alerts/{alert_id}", response_model=dict)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted_alert = await Alert.delete_by_id(db, alert_id)
        if not deleted_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert deleted successfully", "alert_id": alert_id}
    except SQLAlchemyError as e:
        logger.exception(f"SQL error during deletion of alert ID {alert_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Error occurred during deletion.")
    except Exception as e:
        logger.exception(f"Error occurred while deleting alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

