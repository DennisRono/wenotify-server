from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, case
from sqlalchemy.orm import joinedload
from wenotify.models.crime_report import CrimeReport
from wenotify.models.location import Location
from wenotify.models.user import User
from wenotify.models.evidence import Evidence
from wenotify.models.comment import Comment
from wenotify.enums import ReportStatus, UserRole
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
import json


class AnalyticsController:
    async def get_crime_statistics(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        location_id: Optional[str],
        crime_type: Optional[str],
        current_user,
        db: AsyncSession,
    ):
        # Only law enforcement and admin can access analytics
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

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
            conditions.append(CrimeReport.crime_type == crime_type)

        # Total reports count
        total_reports_stmt = select(func.count(CrimeReport.id)).where(and_(*conditions))
        total_reports = await db.scalar(total_reports_stmt)

        # Reports by status
        status_stats_stmt = (
            select(CrimeReport.status, func.count(CrimeReport.id).label("count"))
            .where(and_(*conditions))
            .group_by(CrimeReport.status)
        )

        status_result = await db.execute(status_stats_stmt)
        status_stats = {row.status: row.count for row in status_result}

        # Reports by crime type
        crime_type_stats_stmt = (
            select(CrimeReport.crime_type, func.count(CrimeReport.id).label("count"))
            .where(and_(*conditions))
            .group_by(CrimeReport.crime_type)
        )

        crime_type_result = await db.execute(crime_type_stats_stmt)
        crime_type_stats = {row.crime_type: row.count for row in crime_type_result}

        # Reports by priority
        priority_stats_stmt = (
            select(
                CrimeReport.priority_level, func.count(CrimeReport.id).label("count")
            )
            .where(and_(*conditions))
            .group_by(CrimeReport.priority_level)
        )

        priority_result = await db.execute(priority_stats_stmt)
        priority_stats = {row.priority_level: row.count for row in priority_result}

        # Average response time (for resolved cases)
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
        avg_response_hours = (
            round(avg_response_time / 3600, 2) if avg_response_time else 0
        )

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "total_reports": total_reports,
            "status_breakdown": status_stats,
            "crime_type_breakdown": crime_type_stats,
            "priority_breakdown": priority_stats,
            "average_response_time_hours": avg_response_hours,
        }

    async def get_trend_analysis(
        self,
        period: str,
        crime_type: Optional[str],
        location_id: Optional[str],
        current_user,
        db: AsyncSession,
    ):
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

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
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Period must be 'daily', 'weekly', or 'monthly'",
            )

        # Build conditions
        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        conditions = [
            CrimeReport.created_at >= start_date,
            CrimeReport.deleted_at.is_(None),
        ]

        if crime_type:
            conditions.append(CrimeReport.crime_type == crime_type)
        if location_id:
            conditions.append(CrimeReport.location_id == location_id)

        # Trend query
        trend_stmt = (
            select(
                date_trunc.label("period"), func.count(CrimeReport.id).label("count")
            )
            .where(and_(*conditions))
            .group_by(date_trunc)
            .order_by(date_trunc)
        )

        result = await db.execute(trend_stmt)
        trend_data = [{"period": row.period, "count": row.count} for row in result]

        return {
            "period_type": period,
            "trend_data": trend_data,
            "filters": {"crime_type": crime_type, "location_id": location_id},
        }

    async def get_hotspot_analysis(
        self,
        radius_km: float,
        min_incidents: int,
        days_back: int,
        current_user,
        db: AsyncSession,
    ):
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Simplified hotspot analysis - group by location
        hotspot_stmt = (
            select(
                Location.id,
                Location.name,
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
                Location.id,
                Location.name,
                Location.latitude,
                Location.longitude,
                Location.county,
                Location.sub_county,
            )
            .having(func.count(CrimeReport.id) >= min_incidents)
            .order_by(func.count(CrimeReport.id).desc())
        )

        result = await db.execute(hotspot_stmt)
        hotspots = []

        for row in result:
            hotspots.append(
                {
                    "location_id": row.id,
                    "location_name": row.name,
                    "latitude": float(row.latitude),
                    "longitude": float(row.longitude),
                    "county": row.county,
                    "sub_county": row.sub_county,
                    "incident_count": row.incident_count,
                    "risk_level": (
                        "HIGH" if row.incident_count >= min_incidents * 2 else "MEDIUM"
                    ),
                }
            )

        return {
            "analysis_period_days": days_back,
            "minimum_incidents": min_incidents,
            "radius_km": radius_km,
            "hotspots": hotspots,
            "total_hotspots": len(hotspots),
        }

    async def get_predictive_analysis(
        self,
        prediction_days: int,
        location_id: Optional[str],
        crime_type: Optional[str],
        current_user,
        db: AsyncSession,
    ):
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

        # Simple prediction based on historical averages
        # In production, this would use machine learning models

        # Get historical data for the same period in previous months
        historical_periods = []
        for months_back in [1, 2, 3, 6]:
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
                conditions.append(CrimeReport.crime_type == crime_type)

            count_stmt = select(func.count(CrimeReport.id)).where(and_(*conditions))
            count = await db.scalar(count_stmt)
            historical_periods.append(count)

        # Calculate prediction (simple average)
        if historical_periods:
            predicted_incidents = sum(historical_periods) / len(historical_periods)
            confidence = max(
                0.5,
                1.0
                - (max(historical_periods) - min(historical_periods))
                / max(historical_periods, 1),
            )
        else:
            predicted_incidents = 0
            confidence = 0.0

        return {
            "prediction_period_days": prediction_days,
            "predicted_incidents": round(predicted_incidents),
            "confidence_score": round(confidence, 2),
            "historical_data": historical_periods,
            "filters": {"location_id": location_id, "crime_type": crime_type},
            "recommendation": self._generate_recommendation(
                predicted_incidents, confidence
            ),
        }

    async def get_dashboard_summary(self, current_user, db: AsyncSession):
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can access analytics",
            )

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        # Today's reports
        today_reports_stmt = select(func.count(CrimeReport.id)).where(
            and_(
                CrimeReport.created_at >= today_start, CrimeReport.deleted_at.is_(None)
            )
        )
        today_reports = await db.scalar(today_reports_stmt)

        # Pending reports
        pending_reports_stmt = select(func.count(CrimeReport.id)).where(
            and_(
                CrimeReport.status == ReportStatus.PENDING,
                CrimeReport.deleted_at.is_(None),
            )
        )
        pending_reports = await db.scalar(pending_reports_stmt)

        # High priority reports
        high_priority_stmt = select(func.count(CrimeReport.id)).where(
            and_(
                CrimeReport.priority_level >= 3,
                CrimeReport.status.in_(
                    [ReportStatus.PENDING, ReportStatus.INVESTIGATING]
                ),
                CrimeReport.deleted_at.is_(None),
            )
        )
        high_priority_reports = await db.scalar(high_priority_stmt)

        # Recent activity (last 7 days trend)
        weekly_trend_stmt = (
            select(
                func.date_trunc("day", CrimeReport.created_at).label("day"),
                func.count(CrimeReport.id).label("count"),
            )
            .where(
                and_(
                    CrimeReport.created_at >= week_start,
                    CrimeReport.deleted_at.is_(None),
                )
            )
            .group_by(func.date_trunc("day", CrimeReport.created_at))
            .order_by("day")
        )

        weekly_result = await db.execute(weekly_trend_stmt)
        weekly_trend = [{"date": row.day, "count": row.count} for row in weekly_result]

        # Top crime types this month
        top_crimes_stmt = (
            select(CrimeReport.crime_type, func.count(CrimeReport.id).label("count"))
            .where(
                and_(
                    CrimeReport.created_at >= month_start,
                    CrimeReport.deleted_at.is_(None),
                )
            )
            .group_by(CrimeReport.crime_type)
            .order_by(func.count(CrimeReport.id).desc())
            .limit(5)
        )

        top_crimes_result = await db.execute(top_crimes_stmt)
        top_crime_types = [
            {"crime_type": row.crime_type, "count": row.count}
            for row in top_crimes_result
        ]

        return {
            "summary": {
                "today_reports": today_reports,
                "pending_reports": pending_reports,
                "high_priority_reports": high_priority_reports,
                "total_active_users": await self._get_active_users_count(db),
            },
            "weekly_trend": weekly_trend,
            "top_crime_types": top_crime_types,
            "last_updated": now,
        }

    def _generate_recommendation(
        self, predicted_incidents: float, confidence: float
    ) -> str:
        """Generate recommendation based on prediction"""
        if confidence < 0.6:
            return "Low confidence prediction. More historical data needed for accurate forecasting."
        elif predicted_incidents > 10:
            return "High incident prediction. Consider increasing patrol presence and preventive measures."
        elif predicted_incidents > 5:
            return "Moderate incident prediction. Monitor situation and maintain standard response readiness."
        else:
            return "Low incident prediction. Standard monitoring recommended."

    async def _get_active_users_count(self, db: AsyncSession) -> int:
        """Get count of active users in the last 30 days"""
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(func.count(User.id)).where(
            and_(User.last_login >= thirty_days_ago, User.deleted_at.is_(None))
        )
        return await db.scalar(stmt) or 0
