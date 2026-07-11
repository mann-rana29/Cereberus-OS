from pydantic import BaseModel
from datetime import datetime

class PermitBase(BaseModel):
    zone_id : str
    work_type : str
    assigned_team : str

class PermitCreate(PermitBase):
    pass

class PermitResponse(PermitBase):
    permid_id : str
    status : str = 'ACTIVE'
    created_at : datetime
