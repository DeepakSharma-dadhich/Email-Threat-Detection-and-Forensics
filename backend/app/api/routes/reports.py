from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

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
):
    """
    Return normalized report-ready data
    for one completed analysis.
    """

    return ReportService(
        db
    ).get_report_data(
        analysis_id
    )