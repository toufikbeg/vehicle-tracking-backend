from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    vehicle_id: str
    vehicle_number: str
    model: Optional[str] = None
    capacity: Optional[int] = None


class VehicleCreate(VehicleBase):
    route_id: Optional[int] = None


class VehicleResponse(VehicleBase):
    id: int
    is_active: bool
    route_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True