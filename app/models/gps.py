from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GPSData(Base):
    """Historical GPS tracking data"""
    __tablename__ = "gps_data"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle_code = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True, default=0.0)
    heading = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vehicle = relationship("Vehicle", back_populates="gps_data")

    __table_args__ = (
        Index("ix_gps_vehicle_timestamp", "vehicle_id", "timestamp"),
        Index("ix_gps_vehicle_code", "vehicle_code"),
    )


class LatestLocation(Base):
    """Stores only the latest GPS location for each vehicle"""
    __tablename__ = "latest_locations"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, unique=True)
    vehicle_code = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True, default=0.0)
    heading = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    vehicle = relationship("Vehicle", back_populates="latest_location")