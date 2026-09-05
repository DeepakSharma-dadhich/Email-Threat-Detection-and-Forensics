from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User

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
    current_user: User = Depends(
        get_current_user
    ),
):
    return DashboardService(
        db
    ).get_summary(
        user_id=current_user.id
    )


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
    current_user: User = Depends(
        get_current_user
    ),
):
    return DashboardService(
        db
    ).get_recent(
        user_id=current_user.id,
        limit=limit,
    )