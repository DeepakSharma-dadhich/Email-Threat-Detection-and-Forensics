from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.email import CommonEmailObject, EmailListResponse
from app.services.email_query_service import EmailQueryService

router = APIRouter()


@router.get("", response_model=EmailListResponse)
def list_emails(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return EmailQueryService(db).list(limit=limit, offset=offset)


@router.get("/{email_id}", response_model=CommonEmailObject)
def get_email(
    email_id: UUID,
    db: Session = Depends(get_db),
):
    return EmailQueryService(db).get(email_id)
