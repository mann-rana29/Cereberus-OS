from pydantic import BaseModel
from datetime import datetime
from models.enums import GasType



class SensorLogBase(BaseModel):
    zone_id : str
    gas_type : GasType
    gas_ppm : float

class SensorLogCreate(SensorLogBase):
    pass

class SensorLogResponse(SensorLogBase):
    id : int
    triggered_at : datetime
