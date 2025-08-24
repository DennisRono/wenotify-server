from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict, field_validator

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)
from wenotify.enums import LocationType


class LocationBase(BaseSchemaCreate):
    """Base fields shared across location schemas."""
    model_config = ConfigDict(from_attributes=True)

    latitude: float
    longitude: float
    address: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None
    postal_code: Optional[str] = None
    location_type: LocationType = LocationType.CRIME_SCENE
    landmark: Optional[str] = None
    description: Optional[str] = None
    accuracy_meters: Optional[float] = None
    source: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < -180 or v > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    pass


class LocationUpdate(BaseSchemaUpdate):
    """Schema for updating an existing location."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None
    postal_code: Optional[str] = None
    location_type: Optional[LocationType] = None
    landmark: Optional[str] = None
    description: Optional[str] = None
    accuracy_meters: Optional[float] = None
    source: Optional[str] = None


class LocationResponse(LocationBase, BaseSchemaResponse):
    """Full schema for returning a location with metadata."""
    id: UUID


class LocationListResponse(BaseSchemaResponse):
    """Lightweight schema for listing locations."""
    id: UUID
    latitude: float
    longitude: float
    city: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None
    location_type: LocationType
    created_at: datetime


class NearbyLocationResponse(LocationListResponse):
    """Schema for nearby location queries with distance."""
    distance_km: float
