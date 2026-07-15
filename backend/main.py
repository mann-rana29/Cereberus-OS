from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.db import init_db
from routers.permit_router import router as permit_router
from routers.telemetry_router import router as telemetry_router
from routers.alerts_router import router as alerts_router
from stream_consumer import run_stream_consumer
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(run_stream_consumer())

app.include_router(permit_router)
app.include_router(telemetry_router)
app.include_router(alerts_router)

@app.get("/")
def root():
    return {"message": "Cerberus OS online"}