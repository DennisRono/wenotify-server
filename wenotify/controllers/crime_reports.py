from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.schemas.crime_reports import CrimeReportCreate, CrimeReportUpdate, CrimeReportStatusUpdate
from uuid import UUID
from typing import Optional


class CrimeReportsController:
    async def create_crime_report(self, report_data: CrimeReportCreate, current_user, db: AsyncSession):
        pass
    
    async def get_crime_reports(self, skip: int, limit: int, status_filter: Optional[str], crime_type: Optional[str], current_user, db: AsyncSession):
        pass
    
    async def get_crime_report(self, report_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def update_crime_report(self, report_id: UUID, report_data: CrimeReportUpdate, current_user, db: AsyncSession):
        pass
    
    async def update_report_status(self, report_id: UUID, status_data: CrimeReportStatusUpdate, current_user, db: AsyncSession):
        pass
    
    async def delete_crime_report(self, report_id: UUID, current_user, db: AsyncSession):
        pass
