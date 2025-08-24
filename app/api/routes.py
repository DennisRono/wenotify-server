from fastapi import APIRouter
from app.api.endpoints.test import test_router
from app.api.endpoints.analytics import analytics_router
from app.api.endpoints.comments import comments_router
from app.api.endpoints.crime_reports import crime_reports_router
from app.api.endpoints.evidence import evidence_router
from app.api.endpoints.locations import locations_router
from app.api.endpoints.notifications import notifications_router
from app.api.endpoints.users import users_router

api_router = APIRouter()

api_router.include_router(test_router, prefix="/test", tags=["Test"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(comments_router, prefix="/comments", tags=["Comments"])
api_router.include_router(crime_reports_router, prefix="/crime-reports", tags=["Crime Reports"])
api_router.include_router(evidence_router, prefix="/evidence", tags=["Evidence"])
api_router.include_router(locations_router, prefix="/locations", tags=["Locations"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
