from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GPSDataCreate(BaseModel):
    vehicle_code: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = Field(None, ge=0)
    heading: Optional[float] = Field(None, ge=0, le=360)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime


class GPSDataResponse(BaseModel):
    id: int
    vehicle_code: str
    latitude: float
    longitude: float
    speed: Optional[float]
    heading: Optional[float]
    altitude: Optional[float]
    timestamp: datetime
    received_at: datetime

    class Config:
        from_attributes = True


class LatestLocationResponse(BaseModel):
    vehicle_code: str
    latitude: float
    longitude: float
    speed: Optional[float]
    heading: Optional[float]
    altitude: Optional[float]
    timestamp: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HistoricalTrackingResponse(BaseModel):
    vehicle_code: str
    total_records: int
    data: List[GPSDataResponse]