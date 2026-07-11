from models.permit import PermitCreate, PermitResponse
from fastapi import HTTPException
from datetime import datetime
import uuid
from db.db import get_connection

def register(request : PermitCreate) -> PermitResponse:
    if request is None:
        raise HTTPException(400, "Permit Input is invalid or empty!") 

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT permit_id FROM permits WHERE zone_id = ? AND work_type = ? and STATUS = ?", (request.zone_id, request.work_type, "ACTIVE"))

        if cursor.fetchone():
            conn.close()
            raise HTTPException(400, "Active permit already exists for this zone and work type")

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
            permit_id=permit_id,
            work_type=request.work_type,
            zone_id=request.zone_id,
            assigned_team=request.assigned_team,
            status="ACTIVE",
            created_at=datetime.now()
        )
    
    except HTTPException:
        raise HTTPException(400, "Active permit already exists for this zone and work type")
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")

def get_active_permits() -> list[PermitResponse]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM permits WHERE status = ?", ("ACTIVE",))

    rows = cursor.fetchall()
    res = []
    for row in rows:
        res.append(convert_to_permit(row))

    conn.close()

    return res

def convert_to_permit(row) -> PermitResponse:
    return PermitResponse(
        permit_id=row["permit_id"],
        zone_id=row["zone_id"],
        work_type=row["work_type"],
        assigned_team=row["assigned_team"],
        status=row["status"],
        created_at=row["created_at"]
    )