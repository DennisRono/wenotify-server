from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from wenotify.controllers.crime_reports import CrimeReportsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.crime_reports import (
    CrimeReportCreate,
    CrimeReportResponse,
    CrimeReportUpdate,
    CrimeReportStatusUpdate,
    CrimeReportListResponse
)

crime_reports_router = APIRouter()
crime_reports_controller = CrimeReportsController()


@crime_reports_router.post("/", response_model=CrimeReportResponse, status_code=status.HTTP_201_CREATED)
async def create_crime_report(
    report_data: CrimeReportCreate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.create_crime_report(report_data, current_user, db)


@crime_reports_router.get("/", response_model=List[CrimeReportListResponse])
async def get_crime_reports(
    current_user: GetCurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.get_crime_reports(skip, limit, status_filter, crime_type, current_user, db)


@crime_reports_router.get("/{report_id}", response_model=CrimeReportResponse)
async def get_crime_report(
    report_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.get_crime_report(report_id, current_user, db)


@crime_reports_router.put("/{report_id}", response_model=CrimeReportResponse)
async def update_crime_report(
    report_id: UUID,
    report_data: CrimeReportUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.update_crime_report(report_id, report_data, current_user, db)


@crime_reports_router.patch("/{report_id}/status", response_model=CrimeReportResponse)
async def update_report_status(
    report_id: UUID,
    status_data: CrimeReportStatusUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.update_report_status(report_id, status_data, current_user, db)


@crime_reports_router.delete("/{report_id}", status_code=status.HTTP_200_OK)
async def delete_crime_report(
    report_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await crime_reports_controller.delete_crime_report(report_id, current_user, db)
