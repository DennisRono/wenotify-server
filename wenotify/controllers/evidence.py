from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload
from wenotify.schemas.evidence import EvidenceUpdate
from wenotify.models.evidence import Evidence
from wenotify.models.crime_report import CrimeReport
from wenotify.enums import EvidenceType, UserRole
from fastapi import HTTPException, status, UploadFile
from uuid import UUID, uuid4
from datetime import datetime, timezone
import os
import aiofiles
from pathlib import Path

class EvidenceController:
    async def upload_evidence(self, report_id: UUID, file: UploadFile, current_user, db: AsyncSession):
        # Verify report exists and user has access
        report_stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(report_stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Access control
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload evidence to your own reports"
            )
        
        # Validate file type and size
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        # Create evidence record
        evidence_id = uuid4()
        file_extension = Path(file.filename).suffix
        file_path = f"evidence/{report_id}/{evidence_id}{file_extension}"
        
        # Determine evidence type based on content type
        if file.content_type.startswith('image/'):
            evidence_type = EvidenceType.PHOTO
        elif file.content_type.startswith('video/'):
            evidence_type = EvidenceType.VIDEO
        else:
            evidence_type = EvidenceType.DOCUMENT
        
        # Save file (in production, use cloud storage)
        os.makedirs(f"uploads/evidence/{report_id}", exist_ok=True)
        file_location = f"uploads/{file_path}"
        
        async with aiofiles.open(file_location, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create evidence record
        new_evidence = Evidence(
            id=evidence_id,
            crime_report_id=report_id,
            evidence_type=evidence_type,
            file_name=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type,
            uploaded_by_id=current_user.id,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by_id=current_user.id
        )
        
        db.add(new_evidence)
        await db.commit()
        await db.refresh(new_evidence)
        return new_evidence
    
    async def get_report_evidence(self, report_id: UUID, current_user, db: AsyncSession):
        # Verify report access
        report_stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(report_stmt)
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
        
        # Get evidence
        stmt = select(Evidence).options(
            joinedload(Evidence.uploaded_by)
        ).where(
            and_(
                Evidence.crime_report_id == report_id,
                Evidence.deleted_at.is_(None)
            )
        ).order_by(Evidence.created_at.desc())
        
        result = await db.execute(stmt)
        evidence_list = result.scalars().all()
        return evidence_list
    
    async def get_evidence(self, evidence_id: UUID, current_user, db: AsyncSession):
        stmt = select(Evidence).options(
            joinedload(Evidence.crime_report),
            joinedload(Evidence.uploaded_by)
        ).where(Evidence.id == evidence_id)
        
        evidence = await db.scalar(stmt)
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found"
            )
        
        # Access control
        if (current_user.role == UserRole.CITIZEN and 
            evidence.crime_report.reporter_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return evidence
    
    async def update_evidence(self, evidence_id: UUID, evidence_data: EvidenceUpdate, current_user, db: AsyncSession):
        stmt = select(Evidence).options(
            joinedload(Evidence.crime_report)
        ).where(Evidence.id == evidence_id)
        
        evidence = await db.scalar(stmt)
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found"
            )
        
        # Permission check
        if (current_user.role == UserRole.CITIZEN and 
            evidence.uploaded_by_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own evidence"
            )
        
        # Update evidence
        update_data = evidence_data.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.now(timezone.utc)
            update_data['updated_by_id'] = current_user.id
            
            stmt = update(Evidence).where(Evidence.id == evidence_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(evidence)
        
        return evidence
    
    async def delete_evidence(self, evidence_id: UUID, current_user, db: AsyncSession):
        stmt = select(Evidence).where(Evidence.id == evidence_id)
        evidence = await db.scalar(stmt)
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found"
            )
        
        # Permission check
        if (current_user.role == UserRole.CITIZEN and 
            evidence.uploaded_by_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own evidence"
            )
        
        # Soft delete
        stmt = update(Evidence).where(Evidence.id == evidence_id).values(
            deleted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Evidence deleted successfully"}
    
    async def get_chain_of_custody(self, evidence_id: UUID, current_user, db: AsyncSession):
        # Only law enforcement can view chain of custody
        if current_user.role not in [UserRole.POLICE_OFFICER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only law enforcement can view chain of custody"
            )
        
        stmt = select(Evidence).options(
            joinedload(Evidence.uploaded_by),
            joinedload(Evidence.verified_by)
        ).where(Evidence.id == evidence_id)
        
        evidence = await db.scalar(stmt)
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found"
            )
        
        # Build chain of custody information
        chain_of_custody = {
            "evidence_id": evidence.id,
            "uploaded_by": evidence.uploaded_by,
            "upload_date": evidence.created_at,
            "verified_by": evidence.verified_by,
            "verification_date": evidence.verified_at,
            "is_verified": evidence.is_verified,
            "hash_value": evidence.hash_value,
            "metadata": evidence.metadata_info
        }
        
        return chain_of_custody
