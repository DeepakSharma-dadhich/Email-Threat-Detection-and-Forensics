from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.mailbox import (
    EmailInvestigationResponse,
    MailboxListResponse,
)

from app.services.mailbox_service import (
    MailboxService,
)


router = APIRouter()


def _list_mailbox(
    status: str,
    db: Session,
    limit: int,
    offset: int,
    search: str | None,
    source: str | None,
) -> MailboxListResponse:

    service = MailboxService(db)

    return service.list_emails(
        status=status,
        limit=limit,
        offset=offset,
        search=search,
        source=source,
    )


@router.get(
    "/inbox",
    response_model=MailboxListResponse,
)
def get_inbox(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    search: str | None = Query(
        default=None,
    ),
    source: str | None = Query(
        default=None,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return _list_mailbox(
        status="inbox",
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        source=source,
    )


@router.get(
    "/review",
    response_model=MailboxListResponse,
)
def get_review(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    search: str | None = Query(
        default=None,
    ),
    source: str | None = Query(
        default=None,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return _list_mailbox(
        status="review",
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        source=source,
    )


@router.get(
    "/quarantine",
    response_model=MailboxListResponse,
)
def get_quarantine(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    search: str | None = Query(
        default=None,
    ),
    source: str | None = Query(
        default=None,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return _list_mailbox(
        status="quarantine",
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        source=source,
    )


@router.get(
    "/blocked",
    response_model=MailboxListResponse,
)
def get_blocked(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    search: str | None = Query(
        default=None,
    ),
    source: str | None = Query(
        default=None,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return _list_mailbox(
        status="blocked",
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        source=source,
    )


@router.get(
    "/emails/{email_id}",
    response_model=(
        EmailInvestigationResponse
    ),
)
def get_email_investigation(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    service = MailboxService(db)

    return service.get_investigation(
        email_id
    )