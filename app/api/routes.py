from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.route import BusRoute
from app.models.vehicle import Vehicle
from app.schemas.route import RouteResponse, RouteCreate
from app.schemas.user import UserAssignment
from app.core.dependencies import get_current_active_user, get_admin_user
from typing import List

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/my-route", response_model=RouteResponse)
async def get_my_route(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the route assigned to the current user"""
    if not current_user.assigned_route_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No route assigned to this user"
        )
    
    result = await db.execute(
        select(BusRoute).where(BusRoute.id == current_user.assigned_route_id)
    )
    route = result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned route not found"
        )
    return route


@router.get("/all", response_model=List[RouteResponse])
async def get_all_routes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: Get all routes"""
    result = await db.execute(select(BusRoute).where(BusRoute.is_active == True))
    return result.scalars().all()


@router.post("/create", response_model=RouteResponse, status_code=201)
async def create_route(
    route_data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: Create a new bus route"""
    route = BusRoute(**route_data.model_dump())
    db.add(route)
    await db.commit()
    await db.refresh(route)
    return route


@router.post("/assign", status_code=200)
async def assign_route_vehicle_to_user(
    assignment: UserAssignment,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: Assign a route and vehicle to a user"""
    result = await db.execute(select(User).where(User.id == assignment.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(BusRoute).where(BusRoute.id == assignment.route_id)
    )
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    result = await db.execute(
        select(Vehicle).where(Vehicle.id == assignment.vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    user.assigned_route_id = route.id
    user.assigned_vehicle_id = vehicle.id
    
    await db.commit()
    
    return {
        "message": f"Route '{route.route_name}' and Vehicle '{vehicle.vehicle_id}' "
                   f"assigned to user '{user.username}' successfully"
    }