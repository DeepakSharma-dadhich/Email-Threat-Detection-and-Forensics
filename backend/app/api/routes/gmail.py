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

from app.schemas.gmail import (
    GmailConnectionResponse,
    GmailImportResponse,
    GmailMessageListResponse,
    GmailProcessResponse,
)

from app.services.gmail_import_service import (
    GmailImportService,
)

from app.services.gmail_processing_service import (
    GmailProcessingService,
)

from app.services.gmail_service import (
    GmailService,
)


router = APIRouter()


@router.get(
    "/status",
    response_model=GmailConnectionResponse,
)
def gmail_connection_status(
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        GmailService(
            user_id=current_user.id
        )
        .connection_status()
    )


@router.get(
    "/messages",
    response_model=GmailMessageListResponse,
)
def gmail_messages(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        GmailService(
            user_id=current_user.id
        )
        .list_messages(
            limit=limit
        )
    )


@router.post(
    "/messages/{gmail_message_id}/import",
    response_model=GmailImportResponse,
)
def import_gmail_message(
    gmail_message_id: str,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    record = (
        GmailImportService(
            db=db,
            user_id=current_user.id,
        )
        .import_message(
            gmail_message_id
        )
    )

    return GmailImportResponse(
        gmail_message_id=(
            gmail_message_id
        ),
        email_id=record.id,
        status="imported",
    )


@router.post(
    "/messages/{gmail_message_id}/process",
    response_model=GmailProcessResponse,
)
def process_gmail_message(
    gmail_message_id: str,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        GmailProcessingService(
            db=db,
            user_id=current_user.id,
        )
        .process_message(
            gmail_message_id
        )
    )