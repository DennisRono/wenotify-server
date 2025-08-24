from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import AnalyticsType

if TYPE_CHECKING:
    pass


class Analytics(Base, BaseMixin):
    """Analytics model for storing crime statistics and insights."""
    
    __tablename__ = "analytics"
    
    # Analytics Classification
    analytics_type: Mapped[AnalyticsType] = mapped_column(
        nullable=False,
        index=True
    )
    
    # Geographic Scope
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
    
    # Time Period
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Metrics
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    count_value: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Additional Data
    category_breakdown: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    insights: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Data Quality
    confidence_level: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    data_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_analytics_type_location', 'analytics_type', 'county', 'sub_county'),
        Index('idx_analytics_period', 'period_start', 'period_end'),
        Index('idx_analytics_metric', 'metric_name', 'analytics_type'),
        Index('idx_analytics_time_type', 'period_start', 'analytics_type'),
    )
