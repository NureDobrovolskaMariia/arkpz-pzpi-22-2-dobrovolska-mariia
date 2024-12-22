from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select
from app.models import UserIncubator
from app.models.incubator import Incubator
from app.schemas.incubator import IncubatorCreate, IncubatorUpdate, IncubatorInDB
from app.database import get_db
from typing import List

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.get("/incubators/", response_model=List[IncubatorInDB])
async def get_all_incubators(db: AsyncSession = Depends(get_db)):
    try:
        incubators = await Incubator.get_all(db)
        if not incubators:
            raise HTTPException(status_code=404, detail="No incubators found")
        return incubators
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/incubators/{incubator_id}", response_model=IncubatorInDB)
async def get_incubator(incubator_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Incubator).where(Incubator.incubator_id == incubator_id)
    result = await db.execute(stmt)
    incubator_from_db = result.scalars().first()

    if not incubator_from_db:
        raise HTTPException(status_code=404, detail="Incubator not found")

    return incubator_from_db


@router.delete("/incubators/{incubator_id}", response_model=dict)
async def delete_incubator(incubator_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted_incubator = await Incubator.delete_by_id(db, incubator_id)

        if not deleted_incubator:
            raise HTTPException(status_code=404, detail="Incubator not found")

        return {"message": "Incubator deleted successfully", "incubator_id": incubator_id}

    except HTTPException as e:
        logger.warning(f"HTTPException occurred: {e.detail}")
        raise

    except Exception as e:
        logger.exception(f"Error occurred while deleting incubator with ID {incubator_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/incubators/with-user/{user_id}", response_model=IncubatorInDB, status_code=status.HTTP_201_CREATED)
async def create_incubator_with_user(user_id: int, incubator: IncubatorCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_incubator = await Incubator.create(db, incubator.dict())
        user_incubator = UserIncubator(user_id=user_id, incubator_id=new_incubator.incubator_id)
        db.add(user_incubator)
        await db.commit()
        await db.refresh(new_incubator)
        return new_incubator
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.put("/incubators/{incubator_id}", response_model=IncubatorInDB)
async def update_incubator(incubator_id: int, incubator_update: IncubatorUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Incubator).where(Incubator.incubator_id == incubator_id)
    result = await db.execute(stmt)
    incubator_from_db = result.scalars().first()

    if not incubator_from_db:
        raise HTTPException(status_code=404, detail="Incubator not found")

    incubator_data = incubator_update.dict(exclude_unset=True)

    logger.debug(f"Incubator data to update: {incubator_data}")

    for key, value in incubator_data.items():
        setattr(incubator_from_db, key, value)

    try:
        await db.commit()
        await db.refresh(incubator_from_db)
        logger.info(f"Incubator with ID {incubator_id} updated successfully.")
    except Exception as e:
        logger.exception(f"Error occurred while updating incubator: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return incubator_from_db
