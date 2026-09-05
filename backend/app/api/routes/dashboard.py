
from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.dashboard import (
    DashboardSummary,
    RecentAnalysisItem,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(
        get_db
    ),
):
    return DashboardService(
        db
    ).get_summary()


@router.get(
    "/recent",
    response_model=list[
        RecentAnalysisItem
    ],
)
def recent_analyses(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return DashboardService(
        db
    ).get_recent(
        limit=limit
    )
