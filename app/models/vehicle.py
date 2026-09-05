from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_number = Column(String(50), unique=True, nullable=False)
    model = Column(String(100), nullable=True)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    route_id = Column(Integer, ForeignKey("bus_routes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    route = relationship("BusRoute", back_populates="vehicles")
    assigned_users = relationship("User", back_populates="assigned_vehicle")
    gps_data = relationship("GPSData", back_populates="vehicle")
    latest_location = relationship(
        "LatestLocation",
        back_populates="vehicle",
        uselist=False
    )