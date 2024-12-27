# app/schemas/sensor_reading.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class SensorReadingBase(BaseModel):
    device_id: int
    value_type: str
    value: float
    recorded_at: Optional[datetime]

class SensorReadingCreate(SensorReadingBase):
    @validator('value_type')
    def validate_value_type(cls, v):
        if v and v not in ['temperature', 'humidity']:
            raise ValueError('value_type must be either "temperature" or "humidity"')
        return v

class SensorReadingUpdate(BaseModel):
    value_type: Optional[str] = None
    value: Optional[float] = None
    recorded_at: Optional[datetime] = None

    @validator('value_type')
    def validate_value_type(cls, v):
        if v and v not in ['temperature', 'humidity']:
            raise ValueError('value_type must be either "temperature" or "humidity"')
        return v

class SensorReadingInDB(SensorReadingBase):
    reading_id: int

    class Config:
        orm_mode = True
