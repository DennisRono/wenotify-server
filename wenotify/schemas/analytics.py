from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


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
    percentage: float = Field(default=0.0)


class SeverityStats(BaseModel):
    severity: str
    count: int
    percentage: float


class StatusStats(BaseModel):
    status: str
    count: int
    percentage: float


class CrimeStatsResponse(BaseAnalyticsResponse):
    total_crimes: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    stats_by_type: List[CrimeTypeStats]
    stats_by_location: List[LocationStats]
    stats_by_severity: List[SeverityStats]
    stats_by_status: List[StatusStats]
    average_response_time_hours: float = Field(default=0.0)


# ─── TRENDS ─────────────────────────────────────────────────
class TrendDataPoint(BaseModel):
    period: str  # e.g., "2025-08", "2025-W34", "2025-08-24"
    count: int
    percentage_change: Optional[float] = None


class TrendAnalysisResponse(BaseAnalyticsResponse):
    crime_type: Optional[str]
    location_id: Optional[UUID]
    period: str  # daily, weekly, monthly, yearly
    trends: List[TrendDataPoint]
    total_change_percentage: float = Field(default=0.0)
    trend_direction: str = Field(default="stable")  # increasing, decreasing, stable


# ─── HOTSPOTS ───────────────────────────────────────────────
class HotspotLocation(BaseModel):
    location_id: UUID
    location_name: str
    latitude: float
    longitude: float
    incident_count: int
    risk_level: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    county: Optional[str] = None
    sub_county: Optional[str] = None


class HotspotAnalysisResponse(BaseAnalyticsResponse):
    radius_km: float
    min_incidents: int
    days_back: int
    hotspots: List[HotspotLocation]
    total_hotspots: int


# ─── PREDICTIVE ANALYSIS ────────────────────────────────────
class PredictionDataPoint(BaseModel):
    date: datetime
    predicted_count: int
    confidence: float
    lower_bound: int = Field(default=0)
    upper_bound: int = Field(default=0)


class PredictiveAnalysisResponse(BaseAnalyticsResponse):
    crime_type: Optional[str]
    location_id: Optional[UUID]
    prediction_days: int
    predictions: List[PredictionDataPoint]
    overall_confidence: float = Field(default=0.0)
    recommendation: str = Field(default="")


# ─── DASHBOARD SUMMARY ──────────────────────────────────────
class DashboardSummaryResponse(BaseAnalyticsResponse):
    total_users: int
    active_users: int
    total_reports: int
    resolved_reports: int
    pending_reports: int
    high_priority_reports: int
    today_reports: int
    recent_trends: List[TrendDataPoint]
    top_hotspots: List[HotspotLocation]
    top_crime_types: List[CrimeTypeStats]
    last_updated: datetime


# ─── PERFORMANCE METRICS ────────────────────────────────────
class ResponseTimeMetrics(BaseModel):
    average_response_time_hours: float
    median_response_time_hours: float
    fastest_response_time_hours: float
    slowest_response_time_hours: float
    total_resolved_cases: int


class OfficerPerformanceStats(BaseModel):
    officer_id: UUID
    officer_name: str
    assigned_cases: int
    resolved_cases: int
    average_resolution_time_hours: float
    success_rate: float


class PerformanceAnalyticsResponse(BaseAnalyticsResponse):
    response_time_metrics: ResponseTimeMetrics
    officer_performance: List[OfficerPerformanceStats]
    department_efficiency_score: float = Field(default=0.0)


# ─── GEOGRAPHIC ANALYTICS ───────────────────────────────────
class GeographicStats(BaseModel):
    county: str
    sub_county: Optional[str]
    total_incidents: int
    incidents_per_capita: float = Field(default=0.0)
    most_common_crime: str
    safety_score: float = Field(default=0.0)


class GeographicAnalyticsResponse(BaseAnalyticsResponse):
    geographic_breakdown: List[GeographicStats]
    safest_areas: List[GeographicStats]
    most_dangerous_areas: List[GeographicStats]


# ─── TIME-BASED ANALYTICS ───────────────────────────────────
class TimePatternStats(BaseModel):
    time_period: str  # hour, day_of_week, month
    period_value: str  # "14:00", "Monday", "January"
    incident_count: int
    percentage: float


class TimeBasedAnalyticsResponse(BaseAnalyticsResponse):
    hourly_patterns: List[TimePatternStats]
    daily_patterns: List[TimePatternStats]
    monthly_patterns: List[TimePatternStats]
    peak_crime_hours: List[str]
    peak_crime_days: List[str]


# ─── COMPARATIVE ANALYTICS ──────────────────────────────────
class ComparisonPeriod(BaseModel):
    period_name: str
    start_date: datetime
    end_date: datetime
    total_incidents: int
    change_percentage: float


class ComparativeAnalyticsResponse(BaseAnalyticsResponse):
    current_period: ComparisonPeriod
    previous_period: ComparisonPeriod
    year_over_year: ComparisonPeriod
    crime_type_comparisons: List[Dict[str, Any]]
    location_comparisons: List[Dict[str, Any]]


# ─── EVIDENCE AND CASE ANALYTICS ────────────────────────────
class EvidenceStats(BaseModel):
    evidence_type: str
    total_count: int
    cases_with_evidence: int
    resolution_rate_with_evidence: float


class CaseAnalyticsResponse(BaseAnalyticsResponse):
    total_cases: int
    cases_with_evidence: int
    evidence_statistics: List[EvidenceStats]
    average_evidence_per_case: float
    resolution_rate_by_evidence_count: Dict[str, float]


# ─── USER ENGAGEMENT ANALYTICS ──────────────────────────────
class UserEngagementStats(BaseModel):
    user_type: str  # CITIZEN, POLICE_OFFICER, ADMIN
    total_users: int
    active_users: int
    engagement_rate: float
    average_reports_per_user: float


class UserEngagementResponse(BaseAnalyticsResponse):
    engagement_by_user_type: List[UserEngagementStats]
    most_active_reporters: List[Dict[str, Any]]
    user_retention_rate: float
    new_user_growth_rate: float
