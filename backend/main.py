from fastapi import FastAPI
from db.db import init_db
from routers.permit_router import router as permit_router

app = FastAPI()

app.include_router(permit_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"message" : "backend is working"}
