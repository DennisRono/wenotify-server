from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, text
from wenotify.schemas.locations import LocationCreate, LocationUpdate
from wenotify.models.location import Location
from wenotify.enums import LocationType, UserRole
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


class LocationsController:
    async def create_location(
        self, location_data: LocationCreate, current_user, db: AsyncSession
    ):
        # Only admin and police officers can create locations
        if current_user.role not in [UserRole.ADMIN, UserRole.POLICE_OFFICER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators and police officers can create locations",
            )

        # Create new location
        new_location = Location(
            id=uuid4(),
            location_type=location_data.location_type,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            address=location_data.address,
            street=location_data.street,
            city=location_data.city,
            county=location_data.county,
            sub_county=location_data.sub_county,
            postal_code=location_data.postal_code,
            landmark=location_data.landmark,
            description=location_data.description,
            accuracy_meters=location_data.accuracy_meters,
            source=location_data.source,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by_id=current_user.user_id,
        )

        db.add(new_location)
        await db.commit()
        await db.refresh(new_location)
        return new_location

    async def get_locations(
        self,
        skip: int,
        limit: int,
        location_type: Optional[str],
        current_user,
        db: AsyncSession,
    ):
        # Build query
        conditions = []

        if location_type:
            conditions.append(Location.location_type == location_type)

        stmt = (
            select(Location)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Location.city.asc())
        )

        result = await db.execute(stmt)
        locations = result.scalars().all()
        return locations

    async def get_nearby_locations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        current_user,
        db: AsyncSession,
    ):
        # Use Haversine formula to calculate distance
        # Note: This is a simplified version. In production, use PostGIS for better performance
        distance_formula = (
            func.acos(
                func.sin(func.radians(latitude))
                * func.sin(func.radians(Location.latitude))
                + func.cos(func.radians(latitude))
                * func.cos(func.radians(Location.latitude))
                * func.cos(func.radians(Location.longitude) - func.radians(longitude))
            )
            * 6371
        )  # Earth's radius in kilometers

        stmt = (
            select(Location, distance_formula.label("distance"))
            .where(and_(Location.is_active == True, distance_formula <= radius_km))
            .order_by("distance")
        )

        result = await db.execute(stmt)
        locations_with_distance = result.all()

        # Format response
        nearby_locations = []
        for location, distance in locations_with_distance:
            location_dict = location.__dict__.copy()
            location_dict["distance_km"] = round(float(distance), 2)
            nearby_locations.append(location_dict)

        return nearby_locations

    async def get_location(self, location_id: UUID, current_user, db: AsyncSession):
        stmt = select(Location).where(Location.id == location_id)
        location = await db.scalar(stmt)

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        return location

    async def update_location(
        self,
        location_id: UUID,
        location_data: LocationUpdate,
        current_user,
        db: AsyncSession,
    ):
        # Only admin and police officers can update locations
        if current_user.role not in [UserRole.ADMIN, UserRole.POLICE_OFFICER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators and police officers can update locations",
            )

        stmt = select(Location).where(Location.id == location_id)
        location = await db.scalar(stmt)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        # Update location
        update_data = location_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            update_data["updated_by_id"] = current_user.user_id

            stmt = (
                update(Location).where(Location.id == location_id).values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(location)

        return location

    async def delete_location(self, location_id: UUID, current_user, db: AsyncSession):
        # Only admin can delete locations
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete locations",
            )

        stmt = select(Location).where(Location.id == location_id)
        location = await db.scalar(stmt)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )

        # Soft delete by marking as inactive
        stmt = (
            update(Location)
            .where(Location.id == location_id)
            .values(
                is_active=False,
                deleted_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                updated_by_id=current_user.user_id,
            )
        )
        await db.execute(stmt)
        await db.commit()

        return {"message": "Location deleted successfully"}
