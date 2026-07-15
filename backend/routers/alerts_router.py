from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/alerts", tags=["alerts"])

latest_alert = None

def set_latest_alert(alert: dict):
    global latest_alert
    latest_alert = alert

@router.get("/stream")
async def alert_stream():
    async def event_generator():
        while True:
            if latest_alert:
                yield f"data: {json.dumps(latest_alert)}\n\n"
            await asyncio.sleep(2)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/latest")
def get_latest_alert():
    return latest_alert or {"message": "No active alerts"}