from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.adapters.eml_file import (
    EmlFileAdapter,
)
from app.api.dependencies import (
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.email import (
    CommonEmailObject,
)
from app.services.email_ingestion_service import (
    EmailIngestionService,
)
from app.services.email_query_service import (
    EmailQueryService,
)


router = APIRouter()


@router.post(
    "/emails",
    response_model=CommonEmailObject,
    status_code=status.HTTP_201_CREATED,
)
async def upload_eml(
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    raw_bytes = await file.read()

    adapter = EmlFileAdapter(
        raw_bytes=raw_bytes,
        filename=file.filename,
    )

    record = EmailIngestionService(
        db
    ).ingest(
        adapter=adapter,
        user_id=current_user.id,
    )

    return EmailQueryService(
        db
    ).get_for_user(
        email_id=record.id,
        user_id=current_user.id,
    )