from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.schemas.locations import LocationCreate, LocationUpdate
from uuid import UUID
from typing import Optional


class LocationsController:
    async def create_location(self, location_data: LocationCreate, current_user, db: AsyncSession):
        pass
    
    async def get_locations(self, skip: int, limit: int, location_type: Optional[str], current_user, db: AsyncSession):
        pass
    
    async def get_nearby_locations(self, latitude: float, longitude: float, radius_km: float, current_user, db: AsyncSession):
        pass
    
    async def get_location(self, location_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def update_location(self, location_id: UUID, location_data: LocationUpdate, current_user, db: AsyncSession):
        pass
    
    async def delete_location(self, location_id: UUID, current_user, db: AsyncSession):
        pass
