from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BaseAnalyticsResponse(BaseModel):
    """Base schema for analytics responses."""
    model_config = ConfigDict(from_attributes=True)


# ─── CRIME STATS ────────────────────────────────────────────
class CrimeTypeStats(BaseModel):
    crime_type: str
    count: int
    percentage: float


class LocationStats(BaseModel):
    location_id: UUID
    location_name: str
    count: int


class CrimeStatsResponse(BaseAnalyticsResponse):
    total_crimes: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    stats_by_type: List[CrimeTypeStats]
    stats_by_location: List[LocationStats]


# ─── TRENDS ─────────────────────────────────────────────────
class TrendDataPoint(BaseModel):
    period: str  # e.g., "2025-08", "2025-W34", "2025-08-24"
    count: int


class TrendAnalysisResponse(BaseAnalyticsResponse):
    crime_type: Optional[str]
    location_id: Optional[UUID]
    period: str  # daily, weekly, monthly, yearly
    trends: List[TrendDataPoint]


# ─── HOTSPOTS ───────────────────────────────────────────────
class HotspotLocation(BaseModel):
    location_id: UUID
    location_name: str
    latitude: float
    longitude: float
    incident_count: int


class HotspotAnalysisResponse(BaseAnalyticsResponse):
    radius_km: float
    min_incidents: int
    days_back: int
    hotspots: List[HotspotLocation]


# ─── PREDICTIVE ANALYSIS ────────────────────────────────────
class PredictionDataPoint(BaseModel):
    date: datetime
    predicted_count: int
    confidence: float


class PredictiveAnalysisResponse(BaseAnalyticsResponse):
    crime_type: Optional[str]
    location_id: Optional[UUID]
    prediction_days: int
    predictions: List[PredictionDataPoint]


# ─── DASHBOARD SUMMARY ──────────────────────────────────────
class DashboardSummaryResponse(BaseAnalyticsResponse):
    total_users: int
    active_users: int
    total_reports: int
    resolved_reports: int
    pending_reports: int
    recent_trends: List[TrendDataPoint]
    top_hotspots: List[HotspotLocation]
