from services.permit_service import get_active_permits_for_zone
from services.llm_service import get_llm_verdict
from routers.alerts_router import set_latest_alert

def evaluate_compound_hazard(zone_id: str, gas_type: str, gas_ppm: float):
    active_permits = get_active_permits_for_zone(zone_id=zone_id)

    if not active_permits:
        return None

    permit_dicts = [p.model_dump() for p in active_permits]
    verdict = get_llm_verdict(zone_id, gas_type, gas_ppm, permit_dicts)

    verdict["zone"] = zone_id
    verdict["gas_type"] = gas_type
    verdict["gas_ppm"] = gas_ppm

    if verdict.get("status_code") == "CRITICAL_HAZARD_VIOLATION":
        set_latest_alert(verdict)

    return verdict