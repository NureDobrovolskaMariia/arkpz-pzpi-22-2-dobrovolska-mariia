#app/schemas/alert_history.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertHistoryBase(BaseModel):
    alert_id: int
    status: str
    changed_at: Optional[datetime] = None
    created_by: str


class AlertHistoryCreate(AlertHistoryBase):
    pass


class AlertHistoryUpdate(BaseModel):
    status: Optional[str] = None
    changed_at: Optional[datetime] = None



class AlertHistoryInDB(AlertHistoryBase):
    history_id: int

    class Config:
        orm_mode = True
