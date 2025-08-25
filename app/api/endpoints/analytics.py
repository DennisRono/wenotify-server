from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from wenotify.controllers.analytics import AnalyticsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.enums import CrimeCategory
from wenotify.schemas.analytics import (
    CrimeStatsResponse,
    TrendAnalysisResponse,
    HotspotAnalysisResponse,
    PredictiveAnalysisResponse,
    DashboardSummaryResponse,
    PerformanceAnalyticsResponse,
    GeographicAnalyticsResponse,
    TimeBasedAnalyticsResponse,
    ComparativeAnalyticsResponse,
    CaseAnalyticsResponse,
    UserEngagementResponse
)

analytics_router = APIRouter()
analytics_controller = AnalyticsController()


@analytics_router.get("/crime-stats", response_model=CrimeStatsResponse)
async def get_crime_statistics(
    current_user: GetCurrentUser,
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    location_id: Optional[str] = Query(None, description="Filter by specific location"),
    crime_type: Optional[CrimeCategory] = Query(None, description="Filter by crime category"),
    db: AsyncSession = Depends(get_async_db),
):
    """Get comprehensive crime statistics with breakdowns by type, location, severity, and status."""
    return await analytics_controller.get_crime_statistics(
        start_date, end_date, location_id, crime_type, current_user, db
    )


@analytics_router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    current_user: GetCurrentUser,
    period: str = Query("monthly", regex="^(daily|weekly|monthly|yearly)$", description="Time period for trend analysis"),
    crime_type: Optional[str] = Query(None, description="Filter by specific crime type"),
    location_id: Optional[str] = Query(None, description="Filter by specific location"),
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze crime trends over time with percentage changes and trend direction."""
    return await analytics_controller.get_trend_analysis(
        period, crime_type, location_id, current_user, db
    )


@analytics_router.get("/hotspots", response_model=HotspotAnalysisResponse)
async def get_hotspot_analysis(
    current_user: GetCurrentUser,
    radius_km: float = Query(5.0, ge=0.1, le=50.0, description="Analysis radius in kilometers"),
    min_incidents: int = Query(5, ge=1, description="Minimum incidents to qualify as hotspot"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_async_db),
):
    """Identify crime hotspots with risk levels and geographic clustering."""
    return await analytics_controller.get_hotspot_analysis(
        radius_km, min_incidents, days_back, current_user, db
    )


@analytics_router.get("/predictions", response_model=PredictiveAnalysisResponse)
async def get_predictive_analysis(
    current_user: GetCurrentUser,
    prediction_days: int = Query(7, ge=1, le=30, description="Number of days to predict"),
    location_id: Optional[str] = Query(None, description="Filter by specific location"),
    crime_type: Optional[str] = Query(None, description="Filter by specific crime type"),
    db: AsyncSession = Depends(get_async_db),
):
    """Generate predictive analysis with confidence intervals and recommendations."""
    return await analytics_controller.get_predictive_analysis(
        prediction_days, location_id, crime_type, current_user, db
    )


@analytics_router.get("/dashboard-summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    """Get comprehensive dashboard summary with key metrics and recent trends."""
    return await analytics_controller.get_dashboard_summary(current_user, db)


@analytics_router.get("/performance", response_model=PerformanceAnalyticsResponse)
async def get_performance_analytics(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    """Get detailed performance analytics including response times and officer performance."""
    return await analytics_controller.get_performance_analytics(current_user, db)


@analytics_router.get("/geographic", response_model=GeographicAnalyticsResponse)
async def get_geographic_analytics(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    """Get geographic crime distribution analysis with safety scores."""
    return await analytics_controller.get_geographic_analytics(current_user, db)


@analytics_router.get("/time-patterns", response_model=TimeBasedAnalyticsResponse)
async def get_time_based_analytics(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze crime patterns by time of day, day of week, and month."""
    return await analytics_controller.get_time_based_analytics(current_user, db)


@analytics_router.get("/comparative")
async def get_comparative_analytics(
    current_user: GetCurrentUser,
    compare_period: str = Query("month", regex="^(week|month|quarter|year)$"),
    crime_type: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """Compare current period with previous periods and year-over-year analysis."""
    # Implementation would go in controller
    raise HTTPException(status_code=501, detail="Comparative analytics endpoint coming soon")


@analytics_router.get("/cases")
async def get_case_analytics(
    current_user: GetCurrentUser,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze case resolution rates and evidence effectiveness."""
    # Implementation would go in controller
    raise HTTPException(status_code=501, detail="Case analytics endpoint coming soon")


@analytics_router.get("/user-engagement")
async def get_user_engagement_analytics(
    current_user: GetCurrentUser,
    period_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze user engagement patterns and reporting behavior."""
    # Implementation would go in controller
    raise HTTPException(status_code=501, detail="User engagement analytics endpoint coming soon")


@analytics_router.get("/real-time")
async def get_real_time_analytics(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    """Get real-time crime statistics and active incidents."""
    # Implementation would go in controller
    raise HTTPException(status_code=501, detail="Real-time analytics endpoint coming soon")


@analytics_router.get("/export")
async def export_analytics_data(
    current_user: GetCurrentUser,
    report_type: str = Query("crime-stats", regex="^(crime-stats|trends|hotspots|performance)$"),
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """Export analytics data in various formats."""
    # Implementation would go in controller
    raise HTTPException(status_code=501, detail="Export analytics endpoint coming soon")

