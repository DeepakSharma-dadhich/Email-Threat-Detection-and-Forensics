from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User

from app.schemas.report import (
    ReportDataResponse,
)

from app.services.report_service import (
    ReportService,
)


router = APIRouter()


@router.get(
    "/analyses/{analysis_id}",
    response_model=ReportDataResponse,
)
def get_report_data(
    analysis_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return ReportService(
        db
    ).get_report_data(
        analysis_id=analysis_id,
        user_id=current_user.id,
    )