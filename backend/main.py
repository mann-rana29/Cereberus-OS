from fastapi import FastAPI
from db.db import init_db
from routers.permit_router import router as permit_router
from routers.telemetry_router import router as telemetry_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(permit_router)
app.include_router(telemetry_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"message" : "backend is working"}
