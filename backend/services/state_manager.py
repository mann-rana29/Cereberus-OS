from fastapi import HTTPException
from models.permit import PermitResponse
from models.telemetry import SensorLogResponse
from services.permit_service import get_active_permits_for_zone

def evaluate_compound_hazard(zone_id : str, gas_type: str, gas_ppm: float):
    active_permits = get_active_permits_for_zone(zone_id=zone_id)

    if not active_permits:
        return None
    
    return{
        "status_code" : "CRITICAL_HAZARD_VIOLATION",
        "zone_id" : zone_id,
        "hazard_factor" : f"{gas_type} at {gas_ppm} with active work"
    }