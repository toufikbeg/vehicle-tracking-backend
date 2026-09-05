from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BusRoute(Base):
    __tablename__ = "bus_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(100), nullable=False)
    route_code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_location = Column(String(200), nullable=False)
    end_location = Column(String(200), nullable=False)
    waypoints = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assigned_users = relationship("User", back_populates="assigned_route")
    vehicles = relationship("Vehicle", back_populates="route")