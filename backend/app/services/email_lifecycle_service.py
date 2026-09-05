from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

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
    LifecycleAction,
    LifecycleSummary,
)


class EmailLifecycleService:

    RECOMMENDATION_STATUS_MAP = {
        "allow": EmailOperationalStatus.INBOX,
        "allow_with_monitoring": EmailOperationalStatus.INBOX,
        "review": EmailOperationalStatus.REVIEW,
        "quarantine": EmailOperationalStatus.QUARANTINE,
        "block": EmailOperationalStatus.BLOCKED,
    }

    RECOMMENDATION_ACTION_MAP = {
        "allow": LifecycleAction.SYSTEM_ALLOW,
        "allow_with_monitoring": LifecycleAction.SYSTEM_MONITOR,
        "review": LifecycleAction.SYSTEM_REVIEW,
        "quarantine": LifecycleAction.SYSTEM_QUARANTINE,
        "block": LifecycleAction.SYSTEM_BLOCK,
    }

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.repository = (
            EmailLifecycleRepository(
                db
            )
        )

    def _ensure_email_exists(
        self,
        email_id: UUID,
    ) -> None:

        email = self.db.get(
            EmailRecord,
            email_id,
        )

        if email is None:
            raise HTTPException(
                status_code=404,
                detail="Email not found.",
            )

    def apply_system_decision(
        self,
        email_id: UUID,
        analysis_id: UUID,
        recommended_action: str,
    ) -> EmailLifecycleResponse:

        self._ensure_email_exists(
            email_id
        )

        new_status = (
            self.RECOMMENDATION_STATUS_MAP
            .get(
                recommended_action
            )
        )

        action = (
            self.RECOMMENDATION_ACTION_MAP
            .get(
                recommended_action
            )
        )

        if (
            new_status is None
            or action is None
        ):
            raise ValueError(
                f"Unsupported recommended action: "
                f"{recommended_action}"
            )

        return self._set_state(
            email_id=email_id,
            new_status=new_status,
            action=action,
            actor_type="system",
            reason=(
                "Applied automatically from "
                f"analysis recommendation: "
                f"{recommended_action}"
            ),
            analysis_id=analysis_id,
        )

    def manual_quarantine(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        return self._manual_change(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.QUARANTINE
            ),
            action=(
                LifecycleAction.MANUAL_QUARANTINE
            ),
            reason=reason,
        )

    def manual_block(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        return self._manual_change(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.BLOCKED
            ),
            action=(
                LifecycleAction.MANUAL_BLOCK
            ),
            reason=reason,
        )

    def manual_review(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        return self._manual_change(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.REVIEW
            ),
            action=(
                LifecycleAction.MANUAL_REVIEW
            ),
            reason=reason,
        )

    def manual_allow(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        return self._manual_change(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.INBOX
            ),
            action=(
                LifecycleAction.MANUAL_ALLOW
            ),
            reason=reason,
        )

    def release(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        current = (
            self.repository.get_state(
                email_id
            )
        )

        if current is None:
            raise HTTPException(
                status_code=404,
                detail="Lifecycle state not found.",
            )

        if current.status not in {
            EmailOperationalStatus.QUARANTINE.value,
            EmailOperationalStatus.REVIEW.value,
        }:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Only quarantined or review emails "
                    "can be released."
                ),
            )

        return self._set_state(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.INBOX
            ),
            action=(
                LifecycleAction.RELEASE
            ),
            actor_type="manual",
            reason=reason,
            analysis_id=(
                current.latest_analysis_id
            ),
        )

    def restore(
        self,
        email_id: UUID,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        current = (
            self.repository.get_state(
                email_id
            )
        )

        if current is None:
            raise HTTPException(
                status_code=404,
                detail="Lifecycle state not found.",
            )

        if (
            current.status
            != EmailOperationalStatus.BLOCKED.value
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Only blocked emails "
                    "can be restored."
                ),
            )

        return self._set_state(
            email_id=email_id,
            new_status=(
                EmailOperationalStatus.INBOX
            ),
            action=(
                LifecycleAction.RESTORE
            ),
            actor_type="manual",
            reason=reason,
            analysis_id=(
                current.latest_analysis_id
            ),
        )

    def _manual_change(
        self,
        email_id: UUID,
        new_status: EmailOperationalStatus,
        action: LifecycleAction,
        reason: str | None,
    ) -> EmailLifecycleResponse:

        self._ensure_email_exists(
            email_id
        )

        current = (
            self.repository.get_state(
                email_id
            )
        )

        analysis_id = (
            current.latest_analysis_id
            if current
            else None
        )

        return self._set_state(
            email_id=email_id,
            new_status=new_status,
            action=action,
            actor_type="manual",
            reason=reason,
            analysis_id=analysis_id,
        )

    def _set_state(
        self,
        email_id: UUID,
        new_status: EmailOperationalStatus,
        action: LifecycleAction,
        actor_type: str,
        reason: str | None,
        analysis_id: UUID | None,
    ) -> EmailLifecycleResponse:

        now = datetime.now(
            timezone.utc
        )

        state = (
            self.repository.get_state(
                email_id
            )
        )

        previous_status = (
            state.status
            if state
            else None
        )

        if state is None:
            state = EmailLifecycleState(
                email_id=email_id,
                status=new_status.value,
                latest_analysis_id=analysis_id,
                updated_by=actor_type,
                updated_at=now,
            )

        else:
            state.status = (
                new_status.value
            )

            if analysis_id is not None:
                state.latest_analysis_id = (
                    analysis_id
                )

            state.updated_by = actor_type
            state.updated_at = now

        self.repository.save_state(
            state
        )

        history = EmailActionHistory(
            email_id=email_id,
            analysis_id=analysis_id,
            action=action.value,
            previous_status=previous_status,
            new_status=new_status.value,
            actor_type=actor_type,
            reason=reason,
            created_at=now,
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

    def get_state(
        self,
        email_id: UUID,
    ) -> EmailLifecycleResponse:

        state = (
            self.repository.get_state(
                email_id
            )
        )

        if state is None:
            raise HTTPException(
                status_code=404,
                detail="Lifecycle state not found.",
            )

        return self._state_response(
            state
        )

    def get_history(
        self,
        email_id: UUID,
    ) -> list[EmailActionHistoryItem]:

        self._ensure_email_exists(
            email_id
        )

        records = (
            self.repository.history_for_email(
                email_id
            )
        )

        return [
            EmailActionHistoryItem(
                action_id=(
                    record.action_id
                ),
                email_id=(
                    record.email_id
                ),
                analysis_id=(
                    record.analysis_id
                ),
                action=(
                    record.action
                ),
                previous_status=(
                    record.previous_status
                ),
                new_status=(
                    record.new_status
                ),
                actor_type=(
                    record.actor_type
                ),
                reason=(
                    record.reason
                ),
                created_at=(
                    record.created_at
                ),
            )
            for record in records
        ]

    def get_summary(
        self,
    ) -> LifecycleSummary:

        counts = (
            self.repository
            .status_counts()
        )

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
            email_id=state.email_id,
            status=state.status,
            latest_analysis_id=(
                state.latest_analysis_id
            ),
            updated_by=(
                state.updated_by
            ),
            updated_at=(
                state.updated_at
            ),
        )