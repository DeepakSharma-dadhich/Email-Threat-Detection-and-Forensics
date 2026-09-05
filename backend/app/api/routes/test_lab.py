from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.adapters.eml_file import EmlFileAdapter
from app.db.session import get_db
from app.schemas.email import CommonEmailObject
from app.services.email_ingestion_service import EmailIngestionService
from app.services.email_query_service import EmailQueryService

router = APIRouter()


@router.post(
    "/emails",
    response_model=CommonEmailObject,
    status_code=status.HTTP_201_CREATED,
)
async def upload_eml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw_bytes = await file.read()

    adapter = EmlFileAdapter(
        raw_bytes=raw_bytes,
        filename=file.filename,
    )
    record = EmailIngestionService(db).ingest(adapter)
    response = EmailQueryService(db).get(record.id)

    return response
