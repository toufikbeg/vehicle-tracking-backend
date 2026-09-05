from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    assigned_route_id: Optional[int] = None
    assigned_vehicle_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserAssignment(BaseModel):
    user_id: int
    route_id: int
    vehicle_id: int