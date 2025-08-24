from typing import TYPE_CHECKING, List

from sqlalchemy import Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import LocationType

if TYPE_CHECKING:
    from wenotify.models.crime_report import CrimeReport


class Location(Base, BaseMixin):
    """Location model for storing geographic information."""
    
    __tablename__ = "locations"
    
    # Geographic Coordinates
    latitude: Mapped[float] = mapped_column(
        Float(precision=10),
        nullable=False,
        index=True
    )
    
    longitude: Mapped[float] = mapped_column(
        Float(precision=11),
        nullable=False,
        index=True
    )
    
    # Address Information
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    street: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )
    
    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    county: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    sub_county: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Location Details
    location_type: Mapped[LocationType] = mapped_column(
        nullable=False,
        index=True,
        default=LocationType.CRIME_SCENE
    )
    
    landmark: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Accuracy and Source
    accuracy_meters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Relationships
    crime_reports: Mapped[List["CrimeReport"]] = relationship(
        "CrimeReport",
        back_populates="location",
        foreign_keys="CrimeReport.location_id"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_location_coordinates', 'latitude', 'longitude'),
        Index('idx_location_admin', 'county', 'sub_county', 'city'),
        Index('idx_location_type_county', 'location_type', 'county'),
    )
