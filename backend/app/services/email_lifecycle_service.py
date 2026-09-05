from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.email_lifecycle import (
    EmailActionHistory,
    EmailLifecycleState,
)
from app.models.email_record import EmailRecord
from app.repositories.email_lifecycle_repository import (
    EmailLifecycleRepository,
)
from app.schemas.email_lifecycle import (
    EmailActionHistoryItem,
    EmailLifecycleResponse,
    EmailOperationalStatus,
    LifecycleSummary,
)


class EmailLifecycleService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = EmailLifecycleRepository(db)

    def apply_system_decision(
        self,
        email_id: UUID,
        analysis_id: UUID,
        recommended_action: str,
    ) -> EmailLifecycleResponse:

        action_value = (
            recommended_action.value
            if hasattr(recommended_action, "value")
            else str(recommended_action)
        )

        status_mapping = {
            "allow": EmailOperationalStatus.INBOX.value,
            "allow_with_monitoring": EmailOperationalStatus.INBOX.value,
            "review": EmailOperationalStatus.REVIEW.value,
            "quarantine": EmailOperationalStatus.QUARANTINE.value,
            "block": EmailOperationalStatus.BLOCKED.value,
        }

        action_mapping = {
            "allow": "system_allow",
            "allow_with_monitoring": "system_monitor",
            "review": "system_review",
            "quarantine": "system_quarantine",
            "block": "system_block",
        }

        new_status = status_mapping.get(
            action_value,
            EmailOperationalStatus.REVIEW.value,
        )

        action = action_mapping.get(
            action_value,
            "system_review",
        )

        return self._transition(
            email_id=email_id,
            new_status=new_status,
            action=action,
            actor_type="system",
            reason="Lifecycle state updated from analysis decision.",
            analysis_id=analysis_id,
        )

    def get_state(
        self,
        email_id: UUID,
    ) -> EmailLifecycleResponse:

        state = self.repository.get_state(
            email_id
        )

        if state is None:
            raise AppError(
                "Email lifecycle state not found.",
                404,
                "LIFECYCLE_NOT_FOUND",
            )

        return self._state_response(
            state
        )

    def get_history(
        self,
        email_id: UUID,
    ) -> list[EmailActionHistoryItem]:

        records = (
            self.repository
            .history_for_email(email_id)
        )

        return [
            self._history_response(record)
            for record in records
        ]

    def get_summary(
        self,
    ) -> LifecycleSummary:

        counts = (
            self.repository
            .status_counts()
        )

        return self._build_summary(
            counts
        )

    def get_summary_for_user(
        self,
        user_id: UUID,
    ) -> LifecycleSummary:

        statement = (
            select(
                EmailLifecycleState.status,
                func.count(
                    EmailLifecycleState.state_id
                ),
            )
            .join(
                EmailRecord,
                EmailRecord.id
                == EmailLifecycleState.email_id,
            )
            .where(
                EmailRecord.user_id
                == user_id
            )
            .group_by(
                EmailLifecycleState.status
            )
        )

        rows = self.db.execute(
            statement
        ).all()

        counts = {
            status: int(count)
            for status, count in rows
        }

        return self._build_summary(
            counts
        )

    def manual_quarantine(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .QUARANTINE.value
            ),
            action="manual_quarantine",
            actor_type="user",
            reason=reason,
        )

    def manual_block(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .BLOCKED.value
            ),
            action="manual_block",
            actor_type="user",
            reason=reason,
        )

    def manual_review(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .REVIEW.value
            ),
            action="manual_review",
            actor_type="user",
            reason=reason,
        )

    def manual_allow(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .INBOX.value
            ),
            action="manual_allow",
            actor_type="user",
            reason=reason,
        )

    def release(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        current = self.repository.get_state(
            email_id
        )

        if current is None:
            raise AppError(
                "Email lifecycle state not found.",
                404,
                "LIFECYCLE_NOT_FOUND",
            )

        allowed_states = {
            EmailOperationalStatus.QUARANTINE.value,
            EmailOperationalStatus.REVIEW.value,
        }

        if current.status not in allowed_states:
            raise AppError(
                "Only quarantined or review emails can be released.",
                409,
                "INVALID_LIFECYCLE_TRANSITION",
            )

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .INBOX.value
            ),
            action="release",
            actor_type="user",
            reason=reason,
        )

    def restore(
        self,
        email_id: UUID,
        reason: str | None = None,
    ) -> EmailLifecycleResponse:

        current = self.repository.get_state(
            email_id
        )

        if current is None:
            raise AppError(
                "Email lifecycle state not found.",
                404,
                "LIFECYCLE_NOT_FOUND",
            )

        if (
            current.status
            != EmailOperationalStatus.BLOCKED.value
        ):
            raise AppError(
                "Only blocked emails can be restored.",
                409,
                "INVALID_LIFECYCLE_TRANSITION",
            )

        return self._transition(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus
                .INBOX.value
            ),
            action="restore",
            actor_type="user",
            reason=reason,
        )

    def _transition(
        self,
        email_id: UUID,
        new_status: str,
        action: str,
        actor_type: str,
        reason: str | None = None,
        analysis_id: UUID | None = None,
    ) -> EmailLifecycleResponse:

        email = self.db.get(
            EmailRecord,
            email_id,
        )

        if email is None:
            raise AppError(
                "Email not found.",
                404,
                "EMAIL_NOT_FOUND",
            )

        state = self.repository.get_state(
            email_id
        )

        previous_status = (
            state.status
            if state is not None
            else None
        )

        if state is None:
            state = EmailLifecycleState(
                email_id=email_id,
                status=new_status,
                latest_analysis_id=analysis_id,
                updated_by=actor_type,
            )
        else:
            state.status = new_status

            if analysis_id is not None:
                state.latest_analysis_id = (
                    analysis_id
                )

            state.updated_by = actor_type

        self.repository.save_state(
            state
        )

        history = EmailActionHistory(
            email_id=email_id,
            analysis_id=analysis_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            actor_type=actor_type,
            reason=reason,
        )

        self.repository.save_history(
            history
        )

        self.repository.commit()

        self.repository.refresh_state(
            state
        )

        return self._state_response(
            state
        )

    @staticmethod
    def _build_summary(
        counts: dict[str, int],
    ) -> LifecycleSummary:

        inbox = counts.get(
            EmailOperationalStatus.INBOX.value,
            0,
        )

        quarantine = counts.get(
            EmailOperationalStatus.QUARANTINE.value,
            0,
        )

        blocked = counts.get(
            EmailOperationalStatus.BLOCKED.value,
            0,
        )

        review = counts.get(
            EmailOperationalStatus.REVIEW.value,
            0,
        )

        return LifecycleSummary(
            inbox=inbox,
            quarantine=quarantine,
            blocked=blocked,
            review=review,
            total=(
                inbox
                + quarantine
                + blocked
                + review
            ),
        )

    @staticmethod
    def _state_response(
        state: EmailLifecycleState,
    ) -> EmailLifecycleResponse:

        return EmailLifecycleResponse(
            state_id=state.state_id,
            email_id=state.email_id,
            status=state.status,
            latest_analysis_id=(
                state.latest_analysis_id
            ),
            updated_by=state.updated_by,
            updated_at=state.updated_at,
        )

    @staticmethod
    def _history_response(
        record: EmailActionHistory,
    ) -> EmailActionHistoryItem:

        return EmailActionHistoryItem(
            action_id=record.action_id,
            email_id=record.email_id,
            analysis_id=record.analysis_id,
            action=record.action,
            previous_status=(
                record.previous_status
            ),
            new_status=record.new_status,
            actor_type=record.actor_type,
            reason=record.reason,
            created_at=record.created_at,
        )