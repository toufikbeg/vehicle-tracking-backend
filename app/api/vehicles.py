from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleResponse, VehicleCreate
from app.core.dependencies import get_current_active_user, get_admin_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/my-vehicle", response_model=VehicleResponse)
async def get_my_vehicle(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the vehicle assigned to the current user"""
    if not current_user.assigned_vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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


@router.post("/create", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: Create a new vehicle"""
    vehicle = Vehicle(**vehicle_data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle