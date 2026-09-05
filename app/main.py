import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import auth, routes, vehicles, gps
from app.core.mqtt_client import mqtt_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting GPS Tracking System...")
    await init_db()
    logger.info("✅ Database initialized")
    mqtt_client.connect()
    logger.info("✅ MQTT client connected")
    yield
    mqtt_client.disconnect()
    logger.info("👋 Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GPS-based Vehicle Tracking System API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(gps.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    return {"message": "GPS Tracking System API", "docs": "/docs"}