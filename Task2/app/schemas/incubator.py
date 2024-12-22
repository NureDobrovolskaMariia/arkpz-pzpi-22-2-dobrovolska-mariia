from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class IncubatorBase(BaseModel):
    incubator_name: str = Field(..., alias="incubator_name")
    capacity: int
    status: str
    filled_at: Optional[date]
    target_temperature: float
    target_humidity: float

class IncubatorCreate(IncubatorBase):
    pass

class IncubatorUpdate(BaseModel):
    incubator_name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    filled_at: Optional[date] = None
    target_temperature: Optional[float] = None
    target_humidity: Optional[float] = None

class IncubatorInDB(IncubatorBase):
    incubator_id: int
    filled_at: date

    class Config:
        orm_mode = True
