from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.gps import (
    GPSDataCreate, GPSDataResponse,
    LatestLocationResponse, HistoricalTrackingResponse
)
from app.core.dependencies import get_current_active_user
from app.services.gps_service import (
    process_gps_data, get_latest_location, get_historical_data
)

router = APIRouter(prefix="/gps", tags=["GPS Tracking"])


async def verify_vehicle_access(
    current_user: User,
    db: AsyncSession
) -> Vehicle:
    """Ensure user can only access their assigned vehicle"""
    if not current_user.assigned_vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No vehicle assigned to this user"
        )
    
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == current_user.assigned_vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned vehicle not found"
        )
    return vehicle


@router.get("/current-location", response_model=LatestLocationResponse)
async def get_current_location(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the latest GPS location of the user's assigned vehicle"""
    vehicle = await verify_vehicle_access(current_user, db)
    latest = await get_latest_location(vehicle.id, db)
    
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GPS data available for this vehicle yet"
        )
    return latest


@router.get("/history", response_model=HistoricalTrackingResponse)
async def get_tracking_history(
    limit: int = Query(default=100, le=500, ge=1),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical GPS tracking data for user's assigned vehicle"""
    vehicle = await verify_vehicle_access(current_user, db)
    history = await get_historical_data(vehicle.id, db, limit=limit, offset=offset)
    
    return HistoricalTrackingResponse(
        vehicle_code=vehicle.vehicle_id,
        total_records=len(history),
        data=history
    )


@router.post("/update", status_code=200)
async def update_gps_via_rest(
    gps_data: GPSDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """REST API endpoint to receive GPS data"""
    await process_gps_data(
        vehicle_code=gps_data.vehicle_code,
        payload=gps_data.model_dump()
    )
    return {"message": "GPS data received and stored successfully"}


@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete dashboard data for Flutter home screen"""
    from app.models.route import BusRoute

    response = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
        },
        "route": None,
        "vehicle": None,
        "latest_location": None,
    }

    if current_user.assigned_route_id:
        route_result = await db.execute(
            select(BusRoute).where(BusRoute.id == current_user.assigned_route_id)
        )
        route = route_result.scalar_one_or_none()
        if route:
            response["route"] = {
                "id": route.id,
                "route_name": route.route_name,
                "route_code": route.route_code,
                "start_location": route.start_location,
                "end_location": route.end_location,
                "waypoints": route.waypoints,
            }

    if current_user.assigned_vehicle_id:
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.id == current_user.assigned_vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        if vehicle:
            response["vehicle"] = {
                "id": vehicle.id,
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_number": vehicle.vehicle_number,
                "model": vehicle.model,
                "is_active": vehicle.is_active,
            }

            latest = await get_latest_location(vehicle.id, db)
            if latest:
                response["latest_location"] = {
                    "latitude": latest.latitude,
                    "longitude": latest.longitude,
                    "speed": latest.speed,
                    "heading": latest.heading,
                    "timestamp": latest.timestamp.isoformat(),
                }

    return response