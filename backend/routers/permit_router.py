from fastapi import APIRouter
from models.permit import PermitCreate, PermitResponse
from fastapi import APIRouter
from services.permit_service import register

router = APIRouter(prefix="/permit", tags=["permit"])

@router.post("/", response_model=PermitResponse)
def register_permit(request : PermitCreate):
    return register(request)
    

