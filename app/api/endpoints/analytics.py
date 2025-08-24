from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from wenotify.controllers.analytics import AnalyticsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.analytics import (
    CrimeStatsResponse,
    TrendAnalysisResponse,
    HotspotAnalysisResponse,
    PredictiveAnalysisResponse
)

analytics_router = APIRouter()
analytics_controller = AnalyticsController()


@analytics_router.get("/crime-stats", response_model=CrimeStatsResponse)
async def get_crime_statistics(
    current_user: GetCurrentUser,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    location_id: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await analytics_controller.get_crime_statistics(start_date, end_date, location_id, crime_type, current_user, db)


@analytics_router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    current_user: GetCurrentUser,
    period: str = Query("monthly", regex="^(daily|weekly|monthly|yearly)$"),
    crime_type: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await analytics_controller.get_trend_analysis(period, crime_type, location_id, current_user, db)


@analytics_router.get("/hotspots", response_model=HotspotAnalysisResponse)
async def get_hotspot_analysis(
    current_user: GetCurrentUser,
    radius_km: float = Query(5.0, ge=0.1, le=50.0),
    min_incidents: int = Query(5, ge=1),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_db),
):
    return await analytics_controller.get_hotspot_analysis(radius_km, min_incidents, days_back, current_user, db)


@analytics_router.get("/predictions", response_model=PredictiveAnalysisResponse)
async def get_predictive_analysis(
    current_user: GetCurrentUser,
    prediction_days: int = Query(7, ge=1, le=30),
    location_id: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await analytics_controller.get_predictive_analysis(prediction_days, location_id, crime_type, current_user, db)


@analytics_router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await analytics_controller.get_dashboard_summary(current_user, db)
