from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.session import (
    get_db,
)

from app.schemas.final_analysis import (
    AnalysisHistoryItem,
    FinalAnalysisResponse,
)

from app.services.analysis_service import (
    AnalysisService,
)


router = APIRouter()


@router.post(
    "/emails/{email_id}",
    response_model=FinalAnalysisResponse,
)
def analyze_email(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Run the complete current email-security
    analysis pipeline and persist the result.
    """

    return AnalysisService(
        db
    ).analyze_email(
        email_id
    )


@router.get(
    "/emails/{email_id}/history",
    response_model=list[
        AnalysisHistoryItem
    ],
)
def get_analysis_history(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Return all previous analyses for an email.
    """

    return AnalysisService(
        db
    ).get_history(
        email_id
    )