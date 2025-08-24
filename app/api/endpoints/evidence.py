from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from wenotify.controllers.evidence import EvidenceController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.evidence import (
    EvidenceResponse,
    EvidenceUpdate,
    EvidenceListResponse
)

evidence_router = APIRouter()
evidence_controller = EvidenceController()


@evidence_router.post("/upload/{report_id}", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    report_id: UUID,
    current_user: GetCurrentUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.upload_evidence(report_id, file, current_user, db)


@evidence_router.get("/report/{report_id}", response_model=List[EvidenceListResponse])
async def get_report_evidence(
    report_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.get_report_evidence(report_id, current_user, db)


@evidence_router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.get_evidence(evidence_id, current_user, db)


@evidence_router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: UUID,
    evidence_data: EvidenceUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.update_evidence(evidence_id, evidence_data, current_user, db)


@evidence_router.delete("/{evidence_id}", status_code=status.HTTP_200_OK)
async def delete_evidence(
    evidence_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.delete_evidence(evidence_id, current_user, db)


@evidence_router.get("/{evidence_id}/chain-of-custody")
async def get_chain_of_custody(
    evidence_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await evidence_controller.get_chain_of_custody(evidence_id, current_user, db)
