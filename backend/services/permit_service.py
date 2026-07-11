from models.permit import PermitCreate, PermitResponse
from fastapi import HTTPException
from datetime import datetime
import uuid
from db.db import get_connection

def register(request : PermitCreate) -> PermitResponse:
    if request is None:
        raise HTTPException(400, "Permit Input is invalid or empty!") 

    conn = get_connection()
    cursor = conn.cursor()

    permit_id = str(uuid.uuid4())
    permit = ( permit_id, request.zone_id, request.work_type, request.assigned_team,"ACTIVE",datetime.now())

    cursor.execute(
        """
            INSERT INTO permits (permit_id,zone_id,work_type,assigned_team,status,created_at) VALUES (?,?,?,?,?,?)
        """, permit
    )

    conn.commit()
    conn.close()

    return PermitResponse(
        permid_id=permit_id,
        work_type=request.work_type,
        zone_id=request.zone_id,
        assigned_team=request.assigned_team,
        status="ACTIVE",
        created_at=datetime.now()
    )