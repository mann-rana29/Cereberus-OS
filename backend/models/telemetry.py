from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class GasType(str, Enum):
    CO = "CO"
    H2S = "H2S"
    CH4 = "CH4"
    O2 = "O2"
    SO2 = "SO2"

class SensorLogBase(BaseModel):
    zone_id : str
    gas_type : GasType
    gas_ppm : float

class SensorLogCreate(SensorLogBase):
    pass

class SensorLogResponse(SensorLogBase):
    id : int
    triggered_at : datetime
