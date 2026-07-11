from pydantic import BaseModel
from datetime import datetime
from models.enums import WorkType, PermitStatus

class PermitBase(BaseModel):
    zone_id : str
    work_type : WorkType
    assigned_team : str

class PermitCreate(PermitBase):
    pass

class PermitResponse(PermitBase):
    permit_id : str
    status : PermitStatus = 'ACTIVE'
    created_at : datetime
