from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.email_lifecycle import (
    EmailActionHistory,
    EmailLifecycleState,
)


class EmailLifecycleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_state(
        self,
        email_id: UUID,
    ) -> EmailLifecycleState | None:

        statement = (
            select(EmailLifecycleState)
            .where(
                EmailLifecycleState.email_id == email_id
            )
        )

        return self.db.scalar(statement)

    def save_state(
        self,
        state: EmailLifecycleState,
    ) -> EmailLifecycleState:

        self.db.add(state)
        self.db.flush()

        return state

    def save_history(
        self,
        history: EmailActionHistory,
    ) -> EmailActionHistory:

        self.db.add(history)
        self.db.flush()

        return history

    def commit(self) -> None:
        self.db.commit()

    def refresh_state(
        self,
        state: EmailLifecycleState,
    ) -> None:

        self.db.refresh(state)

    def history_for_email(
        self,
        email_id: UUID,
    ) -> list[EmailActionHistory]:

        statement = (
            select(EmailActionHistory)
            .where(
                EmailActionHistory.email_id == email_id
            )
            .order_by(
                EmailActionHistory.created_at.desc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def status_counts(
        self,
    ) -> dict[str, int]:

        statement = (
            select(
                EmailLifecycleState.status,
                func.count(
                    EmailLifecycleState.state_id
                ),
            )
            .group_by(
                EmailLifecycleState.status
            )
        )

        rows = self.db.execute(
            statement
        ).all()

        return {
            status: int(count)
            for status, count in rows
        }