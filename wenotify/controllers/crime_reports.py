from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List

from wenotify.schemas.crime_reports import (
    CrimeReportCreate,
    CrimeReportUpdate,
    CrimeReportStatusUpdate,
)
from wenotify.models.crime_report import CrimeReport
from wenotify.models.location import Location
from wenotify.models.user import User
from wenotify.enums import ReportStatus, UserRole


class CrimeReportsController:
    async def create_crime_report(
        self, report_data: CrimeReportCreate, current_user, db: AsyncSession
    ):
        # Validate location
        location_stmt = select(Location).where(Location.id == report_data.location_id)
        location = await db.scalar(location_stmt)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )

        # Create new report number
        report_number = f"CR-{uuid4().hex[:10].upper()}"

        # Create crime report
        new_report = CrimeReport(
            id=uuid4(),
            report_number=report_number,
            reporter_id=current_user.user_id,
            is_anonymous=report_data.is_anonymous,
            title=report_data.title,
            description=report_data.description,
            category=report_data.category,
            severity=report_data.severity,
            status=ReportStatus.SUBMITTED,
            location_id=report_data.location_id,
            is_emergency=report_data.is_emergency,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return new_report

    async def get_crime_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        category: Optional[str] = None,
        current_user=None,
        db: AsyncSession = None,
    ):
        stmt = select(CrimeReport).options(
            joinedload(CrimeReport.location),
            joinedload(CrimeReport.reporter),
            joinedload(CrimeReport.assigned_officer),
        )

        # Apply filters
        conditions = []
        if status_filter:
            conditions.append(CrimeReport.status == status_filter)
        if category:
            conditions.append(CrimeReport.category == category)

        # Role-based filtering
        if current_user.role == UserRole.CITIZEN:
            conditions.append(CrimeReport.reporter_id == current_user.user_id)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(CrimeReport.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(stmt)
        reports = result.scalars().all()
        return reports

    async def get_crime_report(
        self, report_id: UUID, current_user, db: AsyncSession
    ):
        stmt = (
            select(CrimeReport)
            .options(
                joinedload(CrimeReport.location),
                joinedload(CrimeReport.reporter),
                joinedload(CrimeReport.assigned_officer),
                selectinload(CrimeReport.evidence),
                selectinload(CrimeReport.comments),
            )
            .where(CrimeReport.id == report_id)
        )

        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found",
            )

        # Access control
        if (
            current_user.role == UserRole.CITIZEN
            and report.reporter_id != current_user.user_id
            and report.is_anonymous
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        return report

    async def update_crime_report(
        self, report_id: UUID, report_data: CrimeReportUpdate, current_user, db: AsyncSession
    ):
        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found",
            )

        # Permission check
        if (
            current_user.role == UserRole.CITIZEN
            and report.reporter_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reports",
            )

        # Update allowed fields
        update_data = report_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)

            stmt = (
                update(CrimeReport)
                .where(CrimeReport.id == report_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(report)

        return report

    async def update_report_status(
        self, report_id: UUID, status_data: CrimeReportStatusUpdate, current_user, db: AsyncSession
    ):
        # Role restriction
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized officers can update report status",
            )

        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found",
            )

        update_values = {
            "status": status_data.status,
            "updated_at": datetime.now(timezone.utc),
        }

        if hasattr(status_data, "assigned_officer_id") and status_data.assigned_officer_id:
            update_values["assigned_officer_id"] = status_data.assigned_officer_id

        stmt = (
            update(CrimeReport)
            .where(CrimeReport.id == report_id)
            .values(**update_values)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(report)
        return report

    async def delete_crime_report(
        self, report_id: UUID, current_user, db: AsyncSession
    ):
        stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found",
            )

        # Permission check
        if (
            current_user.role == UserRole.CITIZEN
            and report.reporter_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reports",
            )

        # Soft delete (if you support that in BaseMixin)
        stmt = (
            update(CrimeReport)
            .where(CrimeReport.id == report_id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await db.execute(stmt)
        await db.commit()

        return {"message": "Crime report deleted successfully"}
