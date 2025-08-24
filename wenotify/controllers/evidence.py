from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.schemas.evidence import EvidenceUpdate
from uuid import UUID
from fastapi import UploadFile


class EvidenceController:
    async def upload_evidence(self, report_id: UUID, file: UploadFile, current_user, db: AsyncSession):
        pass
    
    async def get_report_evidence(self, report_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def get_evidence(self, evidence_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def update_evidence(self, evidence_id: UUID, evidence_data: EvidenceUpdate, current_user, db: AsyncSession):
        pass
    
    async def delete_evidence(self, evidence_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def get_chain_of_custody(self, evidence_id: UUID, current_user, db: AsyncSession):
        pass
