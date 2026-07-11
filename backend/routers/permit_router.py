from fastapi import APIRouter
from models.permit import PermitCreate, PermitResponse
from fastapi import APIRouter
from services.permit_service import register , get_active_permits

router = APIRouter(prefix="/permit", tags=["permit"])

@router.post("/", response_model=PermitResponse)
def register_permit(request : PermitCreate):
    return register(request)

@router.get("/", response_model=list[PermitResponse])
def get_permits():
    return get_active_permits()
    

