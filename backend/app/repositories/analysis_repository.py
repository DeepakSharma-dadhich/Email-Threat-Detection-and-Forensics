from uuid import UUID

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import Session

from app.models.analysis_record import (
    AnalysisRecord,
)


class AnalysisRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        record: AnalysisRecord,
    ) -> AnalysisRecord:

        self.db.add(
            record
        )

        self.db.commit()

        self.db.refresh(
            record
        )

        return record

    def get_by_id(
        self,
        analysis_id: UUID,
    ) -> AnalysisRecord | None:

        statement = (
            select(
                AnalysisRecord
            )
            .where(
                AnalysisRecord.analysis_id
                == analysis_id
            )
        )

        return self.db.scalar(
            statement
        )

    def list_for_email(
        self,
        email_id: UUID,
    ) -> list[AnalysisRecord]:

        statement = (
            select(
                AnalysisRecord
            )
            .where(
                AnalysisRecord.email_id
                == email_id
            )
            .order_by(
                AnalysisRecord.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )