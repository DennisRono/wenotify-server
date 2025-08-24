from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from wenotify.controllers.locations import LocationsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.locations import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    LocationListResponse,
    NearbyLocationResponse
)

locations_router = APIRouter()
locations_controller = LocationsController()


@locations_router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.create_location(location_data, current_user, db)


@locations_router.get("/", response_model=List[LocationListResponse])
async def get_locations(
    current_user: GetCurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.get_locations(skip, limit, location_type, current_user, db)


@locations_router.get("/nearby", response_model=List[NearbyLocationResponse])
async def get_nearby_locations(
    current_user: GetCurrentUser,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100.0),
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.get_nearby_locations(latitude, longitude, radius_km, current_user, db)


@locations_router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.get_location(location_id, current_user, db)


@locations_router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    location_data: LocationUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.update_location(location_id, location_data, current_user, db)


@locations_router.delete("/{location_id}", status_code=status.HTTP_200_OK)
async def delete_location(
    location_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await locations_controller.delete_location(location_id, current_user, db)
