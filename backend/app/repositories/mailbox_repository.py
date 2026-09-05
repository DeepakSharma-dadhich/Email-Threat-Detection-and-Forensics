from uuid import UUID

from sqlalchemy import (
    String,
    cast,
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.models.analysis_record import AnalysisRecord
from app.models.email_lifecycle import (
    EmailActionHistory,
    EmailLifecycleState,
)
from app.models.email_record import EmailRecord


class MailboxRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def list_by_status(
        self,
        user_id: UUID,
        status: str,
        limit: int,
        offset: int,
        search: str | None = None,
        source: str | None = None,
    ) -> tuple[list[tuple], int]:

        conditions = [
            EmailRecord.user_id == user_id,
            EmailLifecycleState.status == status,
        ]

        if source:
            conditions.append(
                EmailRecord.source_type == source
            )

        if search:
            search_value = (
                f"%{search.strip()}%"
            )

            conditions.append(
                or_(
                    EmailRecord.subject.ilike(
                        search_value
                    ),
                    cast(
                        EmailRecord.from_address,
                        String,
                    ).ilike(
                        search_value
                    ),
                )
            )

        count_stmt = (
            select(
                func.count(
                    EmailRecord.id
                )
            )
            .join(
                EmailLifecycleState,
                EmailLifecycleState.email_id
                == EmailRecord.id,
            )
            .where(
                *conditions
            )
        )

        total = (
            self.db.execute(
                count_stmt
            ).scalar_one()
        )

        stmt = (
            select(
                EmailRecord,
                EmailLifecycleState,
                AnalysisRecord,
            )
            .join(
                EmailLifecycleState,
                EmailLifecycleState.email_id
                == EmailRecord.id,
            )
            .outerjoin(
                AnalysisRecord,
                AnalysisRecord.analysis_id
                == EmailLifecycleState.latest_analysis_id,
            )
            .where(
                *conditions
            )
            .order_by(
                EmailRecord.received_at.desc()
                .nullslast(),
                EmailRecord.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        rows = (
            self.db.execute(
                stmt
            )
            .all()
        )

        return rows, total

    def get_email(
        self,
        email_id: UUID,
        user_id: UUID,
    ) -> EmailRecord | None:

        stmt = (
            select(
                EmailRecord
            )
            .where(
                EmailRecord.id == email_id,
                EmailRecord.user_id == user_id,
            )
        )

        return (
            self.db.execute(
                stmt
            ).scalar_one_or_none()
        )

    def get_lifecycle(
        self,
        email_id: UUID,
    ) -> EmailLifecycleState | None:

        stmt = (
            select(
                EmailLifecycleState
            )
            .where(
                EmailLifecycleState.email_id
                == email_id
            )
        )

        return (
            self.db.execute(
                stmt
            ).scalar_one_or_none()
        )

    def get_analysis(
        self,
        analysis_id: UUID | None,
    ) -> AnalysisRecord | None:

        if analysis_id is None:
            return None

        stmt = (
            select(
                AnalysisRecord
            )
            .where(
                AnalysisRecord.analysis_id
                == analysis_id
            )
        )

        return (
            self.db.execute(
                stmt
            ).scalar_one_or_none()
        )

    def list_analysis_history(
        self,
        email_id: UUID,
    ) -> list[AnalysisRecord]:

        stmt = (
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
            self.db.execute(
                stmt
            )
            .scalars()
            .all()
        )

    def list_action_history(
        self,
        email_id: UUID,
    ) -> list[EmailActionHistory]:

        stmt = (
            select(
                EmailActionHistory
            )
            .where(
                EmailActionHistory.email_id
                == email_id
            )
            .order_by(
                EmailActionHistory.created_at.desc()
            )
        )

        return list(
            self.db.execute(
                stmt
            )
            .scalars()
            .all()
        )