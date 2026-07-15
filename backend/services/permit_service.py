from models.permit import PermitCreate, PermitResponse
from fastapi import HTTPException
from datetime import datetime
import uuid
from db.db import get_connection
from models.enums import WorkType
from utils import convert_to_permit

def register(request : PermitCreate) -> PermitResponse:
    if request is None:
        raise HTTPException(400, "Permit Input is invalid or empty!") 

    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT permit_id FROM permits WHERE zone_id = ? AND work_type = ? and STATUS = ?", (request.zone_id, request.work_type, "ACTIVE"))

            if cursor.fetchone():
                raise HTTPException(400, "Active permit already exists for this zone and work type")

            permit_id = str(uuid.uuid4())
            permit = ( permit_id, request.zone_id, request.work_type, request.assigned_team,"ACTIVE",datetime.now())

            cursor.execute(
                """
                    INSERT INTO permits (permit_id,zone_id,work_type,assigned_team,status,created_at) VALUES (?,?,?,?,?,?)
                """, permit
            )

            conn.commit()
        finally:
            conn.close()

        return PermitResponse(
            permit_id=permit_id,
            work_type=request.work_type,
            zone_id=request.zone_id,
            assigned_team=request.assigned_team,
            status="ACTIVE",
            created_at=datetime.now()
        )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")
    
def get_active_permits_for_zone(zone_id : str) -> list[PermitResponse]:
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permits WHERE zone_id = ? AND status = ?", (zone_id,"ACTIVE",))
            rows = cursor.fetchall()
            res = []
            for row in rows:
                res.append(convert_to_permit(row))
            return res
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")

def get_active_permits() -> list[PermitResponse]:
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permits WHERE status = ?", ("ACTIVE",))
            rows = cursor.fetchall()
            res = []
            for row in rows:
                res.append(convert_to_permit(row))
            return res
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")
    
def revoke_permit(zone_id : str, assigned_team : str, work_type : WorkType):
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT permit_id FROM permits WHERE zone_id = ? AND assigned_team = ? AND work_type = ? AND status = 'ACTIVE' ", (zone_id,assigned_team,work_type.value))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(404 , "No active permit found for given details")
            
            permit_id = row["permit_id"]
            cursor.execute("UPDATE permits SET status = 'REVOKED' WHERE permit_id = ? ", (permit_id,))
            conn.commit()
        finally:
            conn.close()

        return {"message" : "Permit revoked successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Database error : {str(e)}")



