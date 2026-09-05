from fastapi import APIRouter

from app.api.routes import (
    analysis,
    dashboard,
    email_lifecycle,
    emails,
    gmail,
    health,
    reports,
    test_lab,
    threat_intelligence,
)
from app.api.routes import mailbox

api_router = APIRouter()


api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    test_lab.router,
    prefix="/test-lab",
    tags=["Test Lab"],
)

api_router.include_router(
    emails.router,
    prefix="/emails",
    tags=["Emails"],
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Analysis"],
)

api_router.include_router(
    email_lifecycle.router,
    prefix="/lifecycle",
    tags=["Email Lifecycle"],
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)

api_router.include_router(
    gmail.router,
    prefix="/gmail",
    tags=["Gmail"],
)
api_router.include_router(
    threat_intelligence.router,
    prefix="/threat-intelligence",
    tags=["Threat Intelligence"],
)

api_router.include_router(
    mailbox.router,
    prefix="/mailbox",
    tags=["Mailbox"],
)