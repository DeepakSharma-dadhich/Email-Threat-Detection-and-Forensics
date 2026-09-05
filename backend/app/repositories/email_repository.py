import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.email_record import EmailRecord


class EmailRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, email_id: uuid.UUID) -> EmailRecord | None:
        return self.db.get(EmailRecord, email_id)


    def create(self, record: EmailRecord) -> EmailRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list(self, limit: int, offset: int) -> tuple[list[EmailRecord], int]:
        items_stmt = (
            select(EmailRecord)
            .order_by(EmailRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        total_stmt = select(func.count()).select_from(EmailRecord)
        return list(self.db.scalars(items_stmt).all()), int(self.db.scalar(total_stmt) or 0)
