from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    incubator_id: int
    message: str
    resolved: Optional[bool] = False


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    message: Optional[str] = None
    resolved: Optional[bool] = None


class AlertInDB(AlertBase):
    alert_id: int
    created_at: datetime

    class Config:
        orm_mode = True
