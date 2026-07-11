from fastapi import APIRouter
from models.telemetry import SensorLogCreate, SensorLogResponse
from services.telemetry_service import get_sensor_logs, ingest_sensor_log
from typing import Optional

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/logs", response_model= list[SensorLogResponse])
def get_logs():
    return get_sensor_logs()

@router.post("/event", response_model=Optional[SensorLogResponse])
def ingest_event(request : SensorLogCreate):
    return ingest_sensor_log(request)