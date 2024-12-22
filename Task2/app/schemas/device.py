from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    device_type: str
    incubator_id: int
    last_reported_at: Optional[datetime]


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    incubator_id: Optional[int] = None
    last_reported_at: Optional[datetime] = None


class DeviceInDB(DeviceBase):
    device_id: int

    class Config:
        orm_mode = True

