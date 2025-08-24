from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    POLICE_OFFICER = "police_officer"
    ADMIN = "admin"
    ANALYST = "analyst"
    DISPATCHER = "dispatcher"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class CrimeCategory(str, Enum):
    THEFT = "theft"
    ASSAULT = "assault"
    BURGLARY = "burglary"
    ROBBERY = "robbery"
    FRAUD = "fraud"
    CYBERCRIME = "cybercrime"
    DOMESTIC_VIOLENCE = "domestic_violence"
    DRUG_RELATED = "drug_related"
    TRAFFIC_VIOLATION = "traffic_violation"
    VANDALISM = "vandalism"
    MURDER = "murder"
    KIDNAPPING = "kidnapping"
    SEXUAL_ASSAULT = "sexual_assault"
    OTHER = "other"


class CrimeSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_INVESTIGATION = "under_investigation"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class EvidenceType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class NotificationType(str, Enum):
    REPORT_SUBMITTED = "report_submitted"
    REPORT_UPDATED = "report_updated"
    REPORT_ASSIGNED = "report_assigned"
    REPORT_RESOLVED = "report_resolved"
    EMERGENCY_ALERT = "emergency_alert"
    SYSTEM_NOTIFICATION = "system_notification"


class NotificationStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class LocationType(str, Enum):
    CRIME_SCENE = "crime_scene"
    LANDMARK = "landmark"
    POLICE_STATION = "police_station"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    PUBLIC_SPACE = "public_space"


class AnalyticsType(str, Enum):
    CRIME_TREND = "crime_trend"
    HOTSPOT_ANALYSIS = "hotspot_analysis"
    RESPONSE_TIME = "response_time"
    RESOLUTION_RATE = "resolution_rate"
    USER_ENGAGEMENT = "user_engagement"
