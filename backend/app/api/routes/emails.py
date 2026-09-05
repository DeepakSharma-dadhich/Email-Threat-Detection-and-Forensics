from uuid import UUID

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
from app.schemas.email import (
    CommonEmailObject,
    EmailListResponse,
)
from app.services.email_query_service import (
    EmailQueryService,
)


router = APIRouter()


@router.get(
    "",
    response_model=EmailListResponse,
)
def list_emails(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return EmailQueryService(
        db
    ).list_for_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{email_id}",
    response_model=CommonEmailObject,
)
def get_email(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return EmailQueryService(
        db
    ).get_for_user(
        email_id=email_id,
        user_id=current_user.id,
    )