from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class RouteBase(BaseModel):
    route_name: str
    route_code: str
    description: Optional[str] = None
    start_location: str
    end_location: str
    waypoints: Optional[List[Dict[str, Any]]] = None


class RouteCreate(RouteBase):
    pass


class RouteResponse(RouteBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True