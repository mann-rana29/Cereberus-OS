from fastapi import APIRouter
from models.permit import PermitCreate, PermitResponse, RevokeRequest
from fastapi import APIRouter
from services.permit_service import register , get_active_permits, revoke_permit

router = APIRouter(prefix="/permit", tags=["permit"])

@router.post("/", response_model=PermitResponse)
def register_permit(request : PermitCreate):
    return register(request)

@router.get("/", response_model=list[PermitResponse])
def get_permits():
    return get_active_permits()
    
@router.patch("/revoke")
def revoke_a_permit(reqeust : RevokeRequest):
    return revoke_permit(reqeust.zone_id,reqeust.assigned_team,reqeust.work_type)
