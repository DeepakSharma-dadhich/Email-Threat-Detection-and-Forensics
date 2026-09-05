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
    current_user: User = Depends(
        get_current_user
    ),
):
    return AnalysisService(
        db
    ).analyze_email(
        email_id=email_id,
        user_id=current_user.id,
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
    current_user: User = Depends(
        get_current_user
    ),
):
    return AnalysisService(
        db
    ).get_history(
        email_id=email_id,
        user_id=current_user.id,
    )