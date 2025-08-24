from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from wenotify.schemas.crime_reports import CrimeReportCreate, CrimeReportUpdate, CrimeReportStatusUpdate
from wenotify.models.crime_report import CrimeReport
from wenotify.models.location import Location
from wenotify.models.user import User
from wenotify.enums import ReportStatus, UserRole
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

class CrimeReportsController:
    async def create_crime_report(self, report_data: CrimeReportCreate, current_user, db: AsyncSession):
        # Validate location if provided
        if report_data.location_id:
            location_stmt = select(Location).where(Location.id == report_data.location_id)
            location = await db.scalar(location_stmt)
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Location not found"
                )
        
        # Create new crime report
        new_report = CrimeReport(
            id=uuid4(),
            title=report_data.title,
            description=report_data.description,
            crime_type=report_data.crime_type,
            incident_date=report_data.incident_date,
            location_id=report_data.location_id,
            latitude=report_data.latitude,
            longitude=report_data.longitude,
            address=report_data.address,
            reporter_id=current_user.id if not report_data.is_anonymous else None,
            is_anonymous=report_data.is_anonymous,
            status=ReportStatus.PENDING,
            priority_level=report_data.priority_level or 1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by_id=current_user.id
        )
        
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return new_report
    
    async def get_crime_reports(self, skip: int, limit: int, status_filter: Optional[str], crime_type: Optional[str], current_user, db: AsyncSession):
        # Build query with filters
        stmt = select(CrimeReport).options(
            joinedload(CrimeReport.location),
            joinedload(CrimeReport.reporter),
            joinedload(CrimeReport.assigned_officer)
        )
        
        # Apply filters
        conditions = []
        if status_filter:
            conditions.append(CrimeReport.status == status_filter)
        if crime_type:
            conditions.append(CrimeReport.crime_type == crime_type)
        
        # Role-based access control
        if current_user.role == UserRole.CITIZEN:
            conditions.append(
                or_(
                    CrimeReport.reporter_id == current_user.id,
                    CrimeReport.is_anonymous == False
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit).order_by(CrimeReport.created_at.desc())
        
        result = await db.execute(stmt)
        reports = result.scalars().all()
        return reports
    
    async def get_crime_report(self, report_id: UUID, current_user, db: AsyncSession):
        stmt = select(CrimeReport).options(
            joinedload(CrimeReport.location),
            joinedload(CrimeReport.reporter),
            joinedload(CrimeReport.assigned_officer),
            selectinload(CrimeReport.evidence),
            selectinload(CrimeReport.comments)
        ).where(CrimeReport.id == report_id)
        
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Access control
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.id and 
            report.is_anonymous):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return report
    
    async def update_crime_report(self, report_id: UUID, report_data: CrimeReportUpdate, current_user, db: AsyncSession):
        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Permission check
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reports"
            )
        
        # Update fields
        update_data = report_data.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.now(timezone.utc)
            update_data['updated_by_id'] = current_user.id
            
            stmt = update(CrimeReport).where(CrimeReport.id == report_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(report)
        
        return report
    
    async def update_report_status(self, report_id: UUID, status_data: CrimeReportStatusUpdate, current_user, db: AsyncSession):
        # Only law enforcement can update status
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can update report status"
            )
        
        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Update status
        update_values = {
            'status': status_data.status,
            'updated_at': datetime.now(timezone.utc),
            'updated_by_id': current_user.id
        }
        
        if status_data.assigned_officer_id:
            update_values['assigned_officer_id'] = status_data.assigned_officer_id
        if status_data.notes:
            update_values['notes'] = status_data.notes
        
        stmt = update(CrimeReport).where(CrimeReport.id == report_id).values(**update_values)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(report)
        
        return report
    
    async def delete_crime_report(self, report_id: UUID, current_user, db: AsyncSession):
        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Permission check
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reports"
            )
        
        # Soft delete
        stmt = update(CrimeReport).where(CrimeReport.id == report_id).values(
            deleted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Crime report deleted successfully"}
