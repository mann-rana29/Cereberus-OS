from fastapi import HTTPException
from models.telemetry import SensorLogResponse , SensorLogCreate
from models.enums import GasType
from db.db import get_connection
from datetime import datetime
from utils import convert_to_sensor_log

THRESHOLDS = {
    "CO" : ("above", 1.5),
    "H2S" : ("above", 5.0),
    "CH4" : ("above" , 1.0),
    "O2" : ("below", 19.5 ),
    "SO2" : ("above" , 2.0)
}

def check_threshold(gas_type : GasType, gas_ppm : float) -> bool:
    direction, limit = THRESHOLDS[gas_type]
    if direction == "above":
        return gas_ppm > limit
    
    return gas_ppm < limit

def ingest_sensor_log(request : SensorLogCreate) -> SensorLogResponse | None:
    try:
        if check_threshold(request.gas_type, request.gas_ppm):
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO sensor_logs (zone_id,gas_type,gas_ppm,triggered_at) VALUES (?,?,?,?)" , (request.zone_id, request.gas_type,request.gas_ppm,datetime.now()))
            
            inserted_id = cursor.lastrowid

            conn.commit()
            conn.close()

            return SensorLogResponse(
                id=inserted_id,
                zone_id=request.zone_id,
                gas_type=request.gas_type,
                gas_ppm=request.gas_ppm,
                triggered_at=datetime.now()
            )
        else:
            return None
        
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")

def get_sensor_logs() -> list[SensorLogResponse]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sensor_logs")
        res = []
        rows = cursor.fetchall()

        for row in rows:
            res.append(convert_to_sensor_log(row))

        return res
    
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")

