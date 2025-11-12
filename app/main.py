from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
from app.api.v1.endpoints import health
from app.worker.consumer import start_consumer

app = FastAPI(
    title="Push Service",
    version="1.0.0",
    description="Push notification service for distributed notification system"
)

Instrumentator().instrument(app).expose(app)

app.include_router(health.router, prefix="/health", tags=["Health"])

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_consumer())

@app.get("/")
def read_root():
    return {"message": "Push Service", "version": "1.0.0"}