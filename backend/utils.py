from models.permit import PermitResponse
from models.telemetry import SensorLogResponse

def convert_to_permit(row) -> PermitResponse:
    return PermitResponse(
        permit_id=row["permit_id"],
        zone_id=row["zone_id"],
        work_type=row["work_type"],
        assigned_team=row["assigned_team"],
        status=row["status"],
        created_at=row["created_at"]
    )

def convert_to_sensor_log(row) -> SensorLogResponse:
    return SensorLogResponse(
        id=row["id"],
        zone_id=row["zone_id"],
        gas_ppm=row["gas_ppm"],
        gas_type=row["gas_type"],
        triggered_at=row["triggered_at"]
    )