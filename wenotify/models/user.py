from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import UserRole, UserStatus

if TYPE_CHECKING:
    from wenotify.models.crime_report import CrimeReport
    from wenotify.models.notification import Notification
    from wenotify.models.comment import Comment


class User(Base, BaseMixin):
    """User model for citizens, police officers, and administrators."""
    
    __tablename__ = "users"
    
    # Basic Information
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    # Role and Status
    role: Mapped[UserRole] = mapped_column(
        nullable=False,
        index=True,
        default=UserRole.CITIZEN
    )
    
    status: Mapped[UserStatus] = mapped_column(
        nullable=False,
        index=True,
        default=UserStatus.PENDING_VERIFICATION
    )
    
    # Profile Information
    profile_picture_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Verification and Security
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Law Enforcement Specific
    badge_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True
    )
    
    department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    rank: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Location Information
    county: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    sub_county: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # Relationships
    submitted_reports: Mapped[List["CrimeReport"]] = relationship(
        "CrimeReport",
        back_populates="reporter",
        foreign_keys="CrimeReport.reporter_id",
        cascade="all, delete-orphan"
    )
    
    assigned_reports: Mapped[List["CrimeReport"]] = relationship(
        "CrimeReport",
        back_populates="assigned_officer",
        foreign_keys="CrimeReport.assigned_officer_id"
    )
    
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id",
        cascade="all, delete-orphan"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        foreign_keys="Comment.author_id",
        cascade="all, delete-orphan"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('phone_number', name='uq_user_phone'),
        UniqueConstraint('badge_number', name='uq_user_badge'),
        Index('idx_user_role_status', 'role', 'status'),
        Index('idx_user_location', 'county', 'sub_county'),
        Index('idx_user_verification', 'is_verified', 'email_verified', 'phone_verified'),
    )
