from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional


class AnalyticsController:
    async def get_crime_statistics(self, start_date: Optional[datetime], end_date: Optional[datetime], location_id: Optional[str], crime_type: Optional[str], current_user, db: AsyncSession):
        pass
    
    async def get_trend_analysis(self, period: str, crime_type: Optional[str], location_id: Optional[str], current_user, db: AsyncSession):
        pass
    
    async def get_hotspot_analysis(self, radius_km: float, min_incidents: int, days_back: int, current_user, db: AsyncSession):
        pass
    
    async def get_predictive_analysis(self, prediction_days: int, location_id: Optional[str], crime_type: Optional[str], current_user, db: AsyncSession):
        pass
    
    async def get_dashboard_summary(self, current_user, db: AsyncSession):
        pass
