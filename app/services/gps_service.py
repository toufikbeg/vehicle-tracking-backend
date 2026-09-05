import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import AsyncSessionLocal
from app.models.vehicle import Vehicle
from app.models.gps import GPSData, LatestLocation

logger = logging.getLogger(__name__)


async def process_gps_data(vehicle_code: str, payload: dict):
    """Process incoming GPS data from MQTT and store in database"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Vehicle).where(Vehicle.vehicle_id == vehicle_code)
            )
            vehicle = result.scalar_one_or_none()

            if not vehicle:
                logger.warning(f"Vehicle not found: {vehicle_code}")
                return

            timestamp = payload.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                )
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()

            latitude = float(payload["latitude"])
            longitude = float(payload["longitude"])
            speed = float(payload.get("speed", 0.0))
            heading = payload.get("heading")
            altitude = payload.get("altitude")
            accuracy = payload.get("accuracy")

            # 1. Store historical GPS data
            gps_record = GPSData(
                vehicle_id=vehicle.id,
                vehicle_code=vehicle_code,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                altitude=altitude,
                accuracy=accuracy,
                timestamp=timestamp,
            )
            db.add(gps_record)

            # 2. Upsert latest location
            result = await db.execute(
                select(LatestLocation).where(
                    LatestLocation.vehicle_id == vehicle.id
                )
            )
            latest = result.scalar_one_or_none()

            if latest:
                latest.latitude = latitude
                latest.longitude = longitude
                latest.speed = speed
                latest.heading = heading
                latest.altitude = altitude
                latest.timestamp = timestamp
            else:
                latest_location = LatestLocation(
                    vehicle_id=vehicle.id,
                    vehicle_code=vehicle_code,
                    latitude=latitude,
                    longitude=longitude,
                    speed=speed,
                    heading=heading,
                    altitude=altitude,
                    timestamp=timestamp,
                )
                db.add(latest_location)

            await db.commit()
            logger.info(
                f"✅ GPS data saved for {vehicle_code}: "
                f"({latitude}, {longitude}) speed={speed}km/h"
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving GPS data: {e}")
            raise


async def get_latest_location(vehicle_id: int, db: AsyncSession) -> Optional[LatestLocation]:
    result = await db.execute(
        select(LatestLocation).where(LatestLocation.vehicle_id == vehicle_id)
    )
    return result.scalar_one_or_none()


async def get_historical_data(
    vehicle_id: int,
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0
) -> List[GPSData]:
    result = await db.execute(
        select(GPSData)
        .where(GPSData.vehicle_id == vehicle_id)
        .order_by(desc(GPSData.timestamp))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()