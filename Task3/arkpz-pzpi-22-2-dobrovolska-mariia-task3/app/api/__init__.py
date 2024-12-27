#app/api/__init.py__
from fastapi import APIRouter
from app.api.user import user_router
from app.api.incubator import router as incubator_router
from app.api.device import router as device_router
from app.api.sensor_reading import router as sensor_reading_router
from app.api.alert import router as alert_router
from app.api.alert_history import router as alert_history_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(incubator_router, prefix="/incubators", tags=["Incubators"])
api_router.include_router(device_router, prefix="/devices", tags=["Devices"])
api_router.include_router(sensor_reading_router, prefix="/sensor-readings", tags=["Sensor Readings"])
api_router.include_router(alert_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(alert_history_router, prefix="/alert-history", tags=["Alert History"])

