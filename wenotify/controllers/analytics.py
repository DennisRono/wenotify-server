from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, case, desc, asc, distinct
from sqlalchemy.orm import joinedload, selectinload
from wenotify.models.crime_report import CrimeReport
from wenotify.models.location import Location
from wenotify.models.user import User
from wenotify.models.evidence import Evidence
from wenotify.models.comment import Comment
from wenotify.models.notification import Notification
from wenotify.models.analytics import Analytics
from wenotify.enums import CrimeCategory, ReportStatus, UserRole, CrimeSeverity, EvidenceType, AnalyticsType
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any, Tuple
import json
import statistics

from wenotify.schemas.analytics import (
    CrimeStatsResponse, TrendAnalysisResponse, HotspotAnalysisResponse,
    PredictiveAnalysisResponse, DashboardSummaryResponse, PerformanceAnalyticsResponse,
    GeographicAnalyticsResponse, TimeBasedAnalyticsResponse, ComparativeAnalyticsResponse,
    CaseAnalyticsResponse, UserEngagementResponse, CrimeTypeStats, LocationStats,
    SeverityStats, StatusStats, TrendDataPoint, HotspotLocation, PredictionDataPoint,
    ResponseTimeMetrics, OfficerPerformanceStats, GeographicStats, TimePatternStats,
    ComparisonPeriod, EvidenceStats, UserEngagementStats
)


class AnalyticsController:
    
    def _check_analytics_permission(self, current_user):
        """Check if user has permission to access analytics"""
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

    async def get_crime_statistics(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        location_id: Optional[str],
        crime_type: Optional[CrimeCategory],
        current_user,
        db: AsyncSession,
    ) -> CrimeStatsResponse:
        self._check_analytics_permission(current_user)

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Build base query conditions
        conditions = [
            CrimeReport.created_at >= start_date,
            CrimeReport.created_at <= end_date,
            CrimeReport.deleted_at.is_(None),
        ]

        if location_id:
            conditions.append(CrimeReport.location_id == location_id)
        if crime_type:
            conditions.append(CrimeReport.category == crime_type)

        # Total reports count
        total_reports_stmt = select(func.count(CrimeReport.id)).where(and_(*conditions))
        total_reports = await db.scalar(total_reports_stmt) or 0

        # Stats by crime type
        type_stats_stmt = (
            select(CrimeReport.category, func.count(CrimeReport.id).label("count"))
            .where(and_(*conditions))
            .group_by(CrimeReport.category)
        )
        type_result = await db.execute(type_stats_stmt)
        stats_by_type = [
            CrimeTypeStats(
                crime_type=row.category.value,
                count=row.count,
                percentage=round((row.count / total_reports) * 100, 2) if total_reports > 0 else 0
            )
            for row in type_result
        ]

        # Stats by location
        location_stats_stmt = (
            select(
                Location.id,
                func.coalesce(Location.city, Location.county, 'Unknown').label("location_name"),
                func.count(CrimeReport.id).label("count")
            )
            .select_from(CrimeReport.__table__.join(Location.__table__))
            .where(and_(*conditions))
            .group_by(Location.id, Location.city, Location.county)
            .order_by(func.count(CrimeReport.id).desc())
        )
        location_result = await db.execute(location_stats_stmt)
        stats_by_location = [
            LocationStats(
                location_id=row.id,
                location_name=row.location_name,
                count=row.count,
                percentage=round((row.count / total_reports) * 100, 2) if total_reports > 0 else 0
            )
            for row in location_result
        ]

        # Stats by severity
        severity_stats_stmt = (
            select(CrimeReport.severity, func.count(CrimeReport.id).label("count"))
            .where(and_(*conditions))
            .group_by(CrimeReport.severity)
        )
        severity_result = await db.execute(severity_stats_stmt)
        stats_by_severity = [
            SeverityStats(
                severity=row.severity.value,
                count=row.count,
                percentage=round((row.count / total_reports) * 100, 2) if total_reports > 0 else 0
            )
            for row in severity_result
        ]

        # Stats by status
        status_stats_stmt = (
            select(CrimeReport.status, func.count(CrimeReport.id).label("count"))
            .where(and_(*conditions))
            .group_by(CrimeReport.status)
        )
        status_result = await db.execute(status_stats_stmt)
        stats_by_status = [
            StatusStats(
                status=row.status.value,
                count=row.count,
                percentage=round((row.count / total_reports) * 100, 2) if total_reports > 0 else 0
            )
            for row in status_result
        ]

        # Average response time
        response_time_stmt = select(
            func.avg(
                func.extract("epoch", CrimeReport.updated_at)
                - func.extract("epoch", CrimeReport.created_at)
            ).label("avg_response_time_seconds")
        ).where(
            and_(
                *conditions,
                CrimeReport.status.in_([ReportStatus.RESOLVED, ReportStatus.CLOSED]),
            )
        )
        avg_response_time = await db.scalar(response_time_stmt)
        avg_response_hours = round(avg_response_time / 3600, 2) if avg_response_time else 0.0

        return CrimeStatsResponse(
            total_crimes=total_reports,
            start_date=start_date,
            end_date=end_date,
            stats_by_type=stats_by_type,
            stats_by_location=stats_by_location,
            stats_by_severity=stats_by_severity,
            stats_by_status=stats_by_status,
            average_response_time_hours=avg_response_hours
        )

    async def get_trend_analysis(
        self,
        period: str,
        crime_type: Optional[str],
        location_id: Optional[str],
        current_user,
        db: AsyncSession,
    ) -> TrendAnalysisResponse:
        self._check_analytics_permission(current_user)

        # Determine date grouping based on period
        if period == "daily":
            date_trunc = func.date_trunc("day", CrimeReport.created_at)
            days_back = 30
        elif period == "weekly":
            date_trunc = func.date_trunc("week", CrimeReport.created_at)
            days_back = 84  # 12 weeks
        elif period == "monthly":
            date_trunc = func.date_trunc("month", CrimeReport.created_at)
            days_back = 365  # 12 months
        elif period == "yearly":
            date_trunc = func.date_trunc("year", CrimeReport.created_at)
            days_back = 1095  # 3 years
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Period must be 'daily', 'weekly', 'monthly', or 'yearly'",
            )

        # Build conditions
        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        conditions = [
            CrimeReport.created_at >= start_date,
            CrimeReport.deleted_at.is_(None),
        ]

        if crime_type:
            conditions.append(CrimeReport.category == crime_type)
        if location_id:
            conditions.append(CrimeReport.location_id == location_id)

        # Trend query
        trend_stmt = (
            select(
                date_trunc.label("period"), 
                func.count(CrimeReport.id).label("count")
            )
            .where(and_(*conditions))
            .group_by(date_trunc)
            .order_by(date_trunc)
        )

        result = await db.execute(trend_stmt)
        trend_data = []
        previous_count = None
        
        for row in result:
            percentage_change = None
            if previous_count is not None and previous_count > 0:
                percentage_change = round(((row.count - previous_count) / previous_count) * 100, 2)
            
            trend_data.append(TrendDataPoint(
                period=row.period.strftime("%Y-%m-%d" if period == "daily" else "%Y-%m" if period == "monthly" else "%Y"),
                count=row.count,
                percentage_change=percentage_change
            ))
            previous_count = row.count

        # Calculate overall trend
        total_change_percentage = 0.0
        trend_direction = "stable"
        if len(trend_data) >= 2:
            first_count = trend_data[0].count
            last_count = trend_data[-1].count
            if first_count > 0:
                total_change_percentage = round(((last_count - first_count) / first_count) * 100, 2)
                if total_change_percentage > 5:
                    trend_direction = "increasing"
                elif total_change_percentage < -5:
                    trend_direction = "decreasing"

        return TrendAnalysisResponse(
            crime_type=crime_type,
            location_id=location_id,
            period=period,
            trends=trend_data,
            total_change_percentage=total_change_percentage,
            trend_direction=trend_direction
        )

    async def get_hotspot_analysis(
        self,
        radius_km: float,
        min_incidents: int,
        days_back: int,
        current_user,
        db: AsyncSession,
    ) -> HotspotAnalysisResponse:
        self._check_analytics_permission(current_user)

        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Hotspot analysis - group by location
        hotspot_stmt = (
            select(
                Location.id,
                func.coalesce(Location.city, Location.county, 'Unknown').label("location_name"),
                Location.latitude,
                Location.longitude,
                Location.county,
                Location.sub_county,
                func.count(CrimeReport.id).label("incident_count"),
            )
            .select_from(CrimeReport.__table__.join(Location.__table__))
            .where(
                and_(
                    CrimeReport.created_at >= start_date,
                    CrimeReport.deleted_at.is_(None),
                )
            )
            .group_by(
                Location.id, Location.city, Location.county,
                Location.latitude, Location.longitude,
                Location.county, Location.sub_county,
            )
            .having(func.count(CrimeReport.id) >= min_incidents)
            .order_by(func.count(CrimeReport.id).desc())
        )

        result = await db.execute(hotspot_stmt)
        hotspots = []

        for row in result:
            # Determine risk level based on incident count
            if row.incident_count >= min_incidents * 4:
                risk_level = "CRITICAL"
            elif row.incident_count >= min_incidents * 2:
                risk_level = "HIGH"
            elif row.incident_count >= min_incidents * 1.5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            hotspots.append(HotspotLocation(
                location_id=row.id,
                location_name=row.location_name,
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                incident_count=row.incident_count,
                risk_level=risk_level,
                county=row.county,
                sub_county=row.sub_county
            ))

        return HotspotAnalysisResponse(
            radius_km=radius_km,
            min_incidents=min_incidents,
            days_back=days_back,
            hotspots=hotspots,
            total_hotspots=len(hotspots)
        )

    async def get_predictive_analysis(
        self,
        prediction_days: int,
        location_id: Optional[str],
        crime_type: Optional[str],
        current_user,
        db: AsyncSession,
    ) -> PredictiveAnalysisResponse:
        self._check_analytics_permission(current_user)

        # Get historical data for prediction
        historical_periods = []
        for months_back in [1, 2, 3, 6, 12]:
            start_date = datetime.now(timezone.utc) - timedelta(
                days=30 * months_back + prediction_days
            )
            end_date = datetime.now(timezone.utc) - timedelta(days=30 * months_back)

            conditions = [
                CrimeReport.created_at >= start_date,
                CrimeReport.created_at <= end_date,
                CrimeReport.deleted_at.is_(None),
            ]

            if location_id:
                conditions.append(CrimeReport.location_id == location_id)
            if crime_type:
                conditions.append(CrimeReport.category == crime_type)

            count_stmt = select(func.count(CrimeReport.id)).where(and_(*conditions))
            count = await db.scalar(count_stmt) or 0
            historical_periods.append(count)

        # Calculate predictions
        predictions = []
        if historical_periods:
            avg_incidents = statistics.mean(historical_periods)
            std_dev = statistics.stdev(historical_periods) if len(historical_periods) > 1 else 0
            
            # Generate daily predictions
            for day in range(prediction_days):
                prediction_date = datetime.now(timezone.utc) + timedelta(days=day + 1)
                
                # Simple prediction with some randomness
                daily_avg = avg_incidents / prediction_days
                predicted_count = max(0, int(daily_avg))
                
                # Calculate confidence based on historical variance
                confidence = max(0.3, 1.0 - (std_dev / max(avg_incidents, 1)))
                
                # Calculate bounds
                lower_bound = max(0, int(daily_avg - std_dev))
                upper_bound = int(daily_avg + std_dev)
                
                predictions.append(PredictionDataPoint(
                    date=prediction_date,
                    predicted_count=predicted_count,
                    confidence=round(confidence, 2),
                    lower_bound=lower_bound,
                    upper_bound=upper_bound
                ))

            overall_confidence = statistics.mean([p.confidence for p in predictions])
            total_predicted = sum([p.predicted_count for p in predictions])
        else:
            overall_confidence = 0.0
            total_predicted = 0

        recommendation = self._generate_recommendation(total_predicted, overall_confidence)

        return PredictiveAnalysisResponse(
            crime_type=crime_type,
            location_id=location_id,
            prediction_days=prediction_days,
            predictions=predictions,
            overall_confidence=round(overall_confidence, 2),
            recommendation=recommendation
        )

    async def get_dashboard_summary(self, current_user, db: AsyncSession) -> DashboardSummaryResponse:
        self._check_analytics_permission(current_user)

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        # Basic counts
        total_users = await db.scalar(select(func.count(User.id)).where(User.deleted_at.is_(None))) or 0
        active_users = await db.scalar(
            select(func.count(User.id)).where(
                and_(User.is_active == True, User.deleted_at.is_(None))
            )
        ) or 0
        
        total_reports = await db.scalar(select(func.count(CrimeReport.id)).where(CrimeReport.deleted_at.is_(None))) or 0
        resolved_reports = await db.scalar(
            select(func.count(CrimeReport.id)).where(
                and_(CrimeReport.status == ReportStatus.RESOLVED, CrimeReport.deleted_at.is_(None))
            )
        ) or 0
        pending_reports = await db.scalar(
            select(func.count(CrimeReport.id)).where(
                and_(CrimeReport.status == ReportStatus.IN_PROGRESS, CrimeReport.deleted_at.is_(None))
            )
        ) or 0
        
        high_priority_reports = await db.scalar(
            select(func.count(CrimeReport.id)).where(
                and_(
                    CrimeReport.priority_score >= 3,
                    CrimeReport.status.in_([ReportStatus.IN_PROGRESS, ReportStatus.UNDER_INVESTIGATION]),
                    CrimeReport.deleted_at.is_(None)
                )
            )
        ) or 0
        
        today_reports = await db.scalar(
            select(func.count(CrimeReport.id)).where(
                and_(CrimeReport.created_at >= today_start, CrimeReport.deleted_at.is_(None))
            )
        ) or 0

        # Recent trends (last 7 days)
        day_trunc = func.date_trunc("day", CrimeReport.created_at).label("day")

        weekly_trend_stmt = (
            select(
                day_trunc,
                func.count(CrimeReport.id).label("count"),
            )
            .where(
                and_(CrimeReport.created_at >= week_start, CrimeReport.deleted_at.is_(None))
            )
            .group_by(day_trunc)
            .order_by(day_trunc)
        )

        weekly_result = await db.execute(weekly_trend_stmt)
        recent_trends = [
            TrendDataPoint(period=row.day.strftime("%Y-%m-%d"), count=row.count)
            for row in weekly_result
        ]

        # Top hotspots (simplified)
        hotspot_stmt = (
            select(
                Location.id,
                func.coalesce(Location.city, Location.county, 'Unknown').label("location_name"),
                Location.latitude,
                Location.longitude,
                func.count(CrimeReport.id).label("incident_count"),
            )
            .select_from(CrimeReport.__table__.join(Location.__table__))
            .where(
                and_(CrimeReport.created_at >= month_start, CrimeReport.deleted_at.is_(None))
            )
            .group_by(Location.id, Location.city, Location.county, Location.latitude, Location.longitude)
            .order_by(func.count(CrimeReport.id).desc())
            .limit(5)
        )
        hotspot_result = await db.execute(hotspot_stmt)
        top_hotspots = [
            HotspotLocation(
                location_id=row.id,
                location_name=row.location_name,
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                incident_count=row.incident_count,
                risk_level="HIGH" if row.incident_count >= 10 else "MEDIUM"
            )
            for row in hotspot_result
        ]

        # Top crime types
        crime_type_stmt = (
            select(CrimeReport.category, func.count(CrimeReport.id).label("count"))
            .where(
                and_(CrimeReport.created_at >= month_start, CrimeReport.deleted_at.is_(None))
            )
            .group_by(CrimeReport.category)
            .order_by(func.count(CrimeReport.id).desc())
            .limit(5)
        )
        crime_type_result = await db.execute(crime_type_stmt)
        top_crime_types = [
            CrimeTypeStats(
                crime_type=row.category.value,
                count=row.count,
                percentage=round((row.count / total_reports) * 100, 2) if total_reports > 0 else 0
            )
            for row in crime_type_result
        ]

        return DashboardSummaryResponse(
            total_users=total_users,
            active_users=active_users,
            total_reports=total_reports,
            resolved_reports=resolved_reports,
            pending_reports=pending_reports,
            high_priority_reports=high_priority_reports,
            today_reports=today_reports,
            recent_trends=recent_trends,
            top_hotspots=top_hotspots,
            top_crime_types=top_crime_types,
            last_updated=now
        )

    async def get_performance_analytics(self, current_user, db: AsyncSession) -> PerformanceAnalyticsResponse:
        self._check_analytics_permission(current_user)

        # Response time metrics
        response_times_stmt = select(
            func.extract("epoch", CrimeReport.updated_at) - func.extract("epoch", CrimeReport.created_at)
        ).where(
            and_(
                CrimeReport.status.in_([ReportStatus.RESOLVED, ReportStatus.CLOSED]),
                CrimeReport.deleted_at.is_(None)
            )
        )
        
        response_times_result = await db.execute(response_times_stmt)
        response_times = [row[0] / 3600 for row in response_times_result if row[0]]  # Convert to hours
        
        if response_times:
            response_time_metrics = ResponseTimeMetrics(
                average_response_time_hours=round(statistics.mean(response_times), 2),
                median_response_time_hours=round(statistics.median(response_times), 2),
                fastest_response_time_hours=round(min(response_times), 2),
                slowest_response_time_hours=round(max(response_times), 2),
                total_resolved_cases=len(response_times)
            )
        else:
            response_time_metrics = ResponseTimeMetrics(
                average_response_time_hours=0.0,
                median_response_time_hours=0.0,
                fastest_response_time_hours=0.0,
                slowest_response_time_hours=0.0,
                total_resolved_cases=0
            )

        # Officer performance
        officer_performance_stmt = (
            select(
                User.id,
                func.concat(User.first_name, ' ', User.last_name).label("officer_name"),
                func.count(CrimeReport.id).label("assigned_cases"),
                func.sum(case((CrimeReport.status.in_([ReportStatus.RESOLVED, ReportStatus.CLOSED]), 1), else_=0)).label("resolved_cases"),
                func.avg(
                    func.extract("epoch", CrimeReport.updated_at) - func.extract("epoch", CrimeReport.created_at)
                ).label("avg_resolution_time")
            )
            .select_from(User.__table__.join(CrimeReport.__table__, User.id == CrimeReport.assigned_officer_id))
            .where(
                and_(
                    User.role == UserRole.POLICE_OFFICER,
                    User.deleted_at.is_(None),
                    CrimeReport.deleted_at.is_(None)
                )
            )
            .group_by(User.id, User.first_name, User.last_name)
            .having(func.count(CrimeReport.id) > 0)
        )
        
        officer_result = await db.execute(officer_performance_stmt)
        officer_performance = []
        
        for row in officer_result:
            success_rate = (row.resolved_cases / row.assigned_cases) * 100 if row.assigned_cases > 0 else 0
            avg_time_hours = row.avg_resolution_time / 3600 if row.avg_resolution_time else 0
            
            officer_performance.append(OfficerPerformanceStats(
                officer_id=row.id,
                officer_name=row.officer_name,
                assigned_cases=row.assigned_cases,
                resolved_cases=row.resolved_cases,
                average_resolution_time_hours=round(avg_time_hours, 2),
                success_rate=round(success_rate, 2)
            ))

        # Department efficiency score (simple calculation)
        total_cases = sum(op.assigned_cases for op in officer_performance)
        total_resolved = sum(op.resolved_cases for op in officer_performance)
        department_efficiency_score = (total_resolved / total_cases) * 100 if total_cases > 0 else 0

        return PerformanceAnalyticsResponse(
            response_time_metrics=response_time_metrics,
            officer_performance=officer_performance,
            department_efficiency_score=round(department_efficiency_score, 2)
        )

    async def get_geographic_analytics(self, current_user, db: AsyncSession) -> GeographicAnalyticsResponse:
        self._check_analytics_permission(current_user)

        # Geographic breakdown
        geographic_stmt = (
            select(
                Location.county,
                Location.sub_county,
                func.count(CrimeReport.id).label("total_incidents"),
                CrimeReport.category
            )
            .select_from(CrimeReport.__table__.join(Location.__table__))
            .where(CrimeReport.deleted_at.is_(None))
            .group_by(Location.county, Location.sub_county, CrimeReport.category)
        )
        
        result = await db.execute(geographic_stmt)
        geographic_data = {}
        
        for row in result:
            key = f"{row.county}_{row.sub_county or 'Unknown'}"
            if key not in geographic_data:
                geographic_data[key] = {
                    'county': row.county,
                    'sub_county': row.sub_county,
                    'total_incidents': 0,
                    'crime_counts': {}
                }
            
            geographic_data[key]['total_incidents'] += row.total_incidents
            geographic_data[key]['crime_counts'][row.category.value] = row.total_incidents

        geographic_breakdown = []
        for data in geographic_data.values():
            most_common_crime = max(data['crime_counts'], key=data['crime_counts'].get) if data['crime_counts'] else "Unknown"
            safety_score = max(0, 100 - (data['total_incidents'] * 2))  # Simple safety score calculation
            
            geographic_breakdown.append(GeographicStats(
                county=data['county'],
                sub_county=data['sub_county'],
                total_incidents=data['total_incidents'],
                incidents_per_capita=0.0,  # Would need population data
                most_common_crime=most_common_crime,
                safety_score=round(safety_score, 2)
            ))

        # Sort for safest and most dangerous areas
        sorted_areas = sorted(geographic_breakdown, key=lambda x: x.total_incidents)
        safest_areas = sorted_areas[:5]
        most_dangerous_areas = sorted_areas[-5:]

        return GeographicAnalyticsResponse(
            geographic_breakdown=geographic_breakdown,
            safest_areas=safest_areas,
            most_dangerous_areas=most_dangerous_areas
        )

    async def get_time_based_analytics(self, current_user, db: AsyncSession) -> TimeBasedAnalyticsResponse:
        self._check_analytics_permission(current_user)

        # Hourly patterns
        hourly_stmt = (
            select(
                func.extract('hour', CrimeReport.created_at).label('hour'),
                func.count(CrimeReport.id).label('count')
            )
            .where(CrimeReport.deleted_at.is_(None))
            .group_by(func.extract('hour', CrimeReport.created_at))
            .order_by('hour')
        )
        
        hourly_result = await db.execute(hourly_stmt)
        total_incidents = sum(row.count for row in hourly_result)
        
        # Re-execute for percentage calculation
        hourly_result = await db.execute(hourly_stmt)
        hourly_patterns = [
            TimePatternStats(
                time_period="hour",
                period_value=f"{int(row.hour):02d}:00",
                incident_count=row.count,
                percentage=round((row.count / total_incidents) * 100, 2) if total_incidents > 0 else 0
            )
            for row in hourly_result
        ]

        # Daily patterns (day of week)
        daily_stmt = (
            select(
                func.extract('dow', CrimeReport.created_at).label('dow'),
                func.count(CrimeReport.id).label('count')
            )
            .where(CrimeReport.deleted_at.is_(None))
            .group_by(func.extract('dow', CrimeReport.created_at))
            .order_by('dow')
        )
        
        daily_result = await db.execute(daily_stmt)
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_patterns = [
            TimePatternStats(
                time_period="day_of_week",
                period_value=day_names[int(row.dow)],
                incident_count=row.count,
                percentage=round((row.count / total_incidents) * 100, 2) if total_incidents > 0 else 0
            )
            for row in daily_result
        ]

        # Monthly patterns
        monthly_stmt = (
            select(
                func.extract('month', CrimeReport.created_at).label('month'),
                func.count(CrimeReport.id).label('count')
            )
            .where(CrimeReport.deleted_at.is_(None))
            .group_by(func.extract('month', CrimeReport.created_at))
            .order_by('month')
        )
        
        monthly_result = await db.execute(monthly_stmt)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_patterns = [
            TimePatternStats(
                time_period="month",
                period_value=month_names[int(row.month) - 1],
                incident_count=row.count,
                percentage=round((row.count / total_incidents) * 100, 2) if total_incidents > 0 else 0
            )
            for row in monthly_result
        ]

        # Peak times
        peak_crime_hours = [pattern.period_value for pattern in sorted(hourly_patterns, key=lambda x: x.incident_count, reverse=True)[:3]]
        peak_crime_days = [pattern.period_value for pattern in sorted(daily_patterns, key=lambda x: x.incident_count, reverse=True)[:3]]

        return TimeBasedAnalyticsResponse(
            hourly_patterns=hourly_patterns,
            daily_patterns=daily_patterns,
            monthly_patterns=monthly_patterns,
            peak_crime_hours=peak_crime_hours,
            peak_crime_days=peak_crime_days
        )

    def _generate_recommendation(self, predicted_incidents: float, confidence: float) -> str:
        """Generate recommendation based on prediction"""
        if confidence < 0.6:
            return "Low confidence prediction. More historical data needed for accurate forecasting."
        elif predicted_incidents > 20:
            return "Very high incident prediction. Consider emergency response protocols and increased patrol presence."
        elif predicted_incidents > 10:
            return "High incident prediction. Consider increasing patrol presence and preventive measures."
        elif predicted_incidents > 5:
            return "Moderate incident prediction. Monitor situation and maintain standard response readiness."
        else:
            return "Low incident prediction. Standard monitoring recommended."
