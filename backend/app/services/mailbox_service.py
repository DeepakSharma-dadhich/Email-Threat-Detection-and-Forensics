from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.mailbox_repository import (
    MailboxRepository,
)

from app.schemas.mailbox import (
    EmailInvestigationResponse,
    InvestigationActionHistoryItem,
    InvestigationAnalysisHistoryItem,
    InvestigationDecision,
    InvestigationLifecycle,
    MailboxEmailItem,
    MailboxLatestAnalysis,
    MailboxListResponse,
)


class MailboxService:

    VALID_STATUSES = {
        "inbox",
        "review",
        "quarantine",
        "blocked",
    }

    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            MailboxRepository(db)
        )

    def list_emails(
        self,
        user_id: UUID,
        status: str,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        source: str | None = None,
    ) -> MailboxListResponse:

        if status not in self.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid mailbox status."
                ),
            )

        rows, total = (
            self.repository.list_by_status(
                user_id=user_id,
                status=status,
                limit=limit,
                offset=offset,
                search=search,
                source=source,
            )
        )

        items = []

        for (
            email,
            lifecycle,
            analysis,
        ) in rows:

            attachments = (
                email.attachments or []
            )

            url_count = (
                self._extract_url_count(
                    analysis
                )
            )

            latest_analysis = None

            if analysis is not None:
                latest_analysis = (
                    MailboxLatestAnalysis(
                        analysis_id=(
                            analysis.analysis_id
                        ),
                        risk_score=(
                            analysis.aggregate_score
                        ),
                        verdict=(
                            analysis.verdict
                        ),
                        recommended_action=(
                            analysis
                            .recommended_action
                        ),
                        analyzed_at=(
                            analysis.created_at
                        ),
                    )
                )

            items.append(
                MailboxEmailItem(
                    email_id=email.id,
                    subject=email.subject,
                    from_address=(
                        email.from_address
                    ),
                    received_at=(
                        email.received_at
                    ),
                    source_type=(
                        email.source_type
                    ),
                    status=(
                        lifecycle.status
                    ),
                    has_attachments=bool(
                        attachments
                    ),
                    attachment_count=len(
                        attachments
                    ),
                    url_count=url_count,
                    latest_analysis=(
                        latest_analysis
                    ),
                )
            )

        return MailboxListResponse(
            status=status,
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    def get_investigation(
        self,
        email_id: UUID,
        user_id: UUID,
    ) -> EmailInvestigationResponse:

        email = (
            self.repository.get_email(
                email_id=email_id,
                user_id=user_id,
            )
        )

        if email is None:
            raise HTTPException(
                status_code=404,
                detail="Email not found.",
            )

        lifecycle = (
            self.repository.get_lifecycle(
                email_id
            )
        )

        if lifecycle is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Lifecycle state not found "
                    "for this email."
                ),
            )

        latest_analysis = (
            self.repository.get_analysis(
                lifecycle.latest_analysis_id
            )
        )

        decision = None
        modules = []

        if latest_analysis is not None:
            decision = InvestigationDecision(
                analysis_id=(
                    latest_analysis.analysis_id
                ),
                risk_score=(
                    latest_analysis
                    .aggregate_score
                ),
                verdict=(
                    latest_analysis.verdict
                ),
                recommended_action=(
                    latest_analysis
                    .recommended_action
                ),
                browser_isolation_recommended=(
                    latest_analysis
                    .browser_isolation_recommended
                ),
                analyzed_at=(
                    latest_analysis.created_at
                ),
            )

            modules = (
                latest_analysis.module_results
                or []
            )

        analysis_records = (
            self.repository
            .list_analysis_history(
                email_id
            )
        )

        action_records = (
            self.repository
            .list_action_history(
                email_id
            )
        )

        analysis_history = [
            InvestigationAnalysisHistoryItem(
                analysis_id=(
                    record.analysis_id
                ),
                risk_score=(
                    record.aggregate_score
                ),
                verdict=record.verdict,
                recommended_action=(
                    record.recommended_action
                ),
                browser_isolation_recommended=(
                    record
                    .browser_isolation_recommended
                ),
                created_at=(
                    record.created_at
                ),
            )
            for record
            in analysis_records
        ]

        action_history = [
            InvestigationActionHistoryItem(
                action_id=(
                    record.action_id
                ),
                analysis_id=(
                    record.analysis_id
                ),
                action=record.action,
                previous_status=(
                    record.previous_status
                ),
                new_status=(
                    record.new_status
                ),
                actor_type=(
                    record.actor_type
                ),
                reason=record.reason,
                created_at=(
                    record.created_at
                ),
            )
            for record
            in action_records
        ]

        return EmailInvestigationResponse(
            email_id=email.id,
            source_type=(
                email.source_type
            ),
            source_message_id=(
                email.source_message_id
            ),
            message_id=(
                email.message_id
            ),
            subject=email.subject,
            from_address=(
                email.from_address
            ),
            reply_to=email.reply_to,
            return_path=(
                email.return_path
            ),
            to_addresses=(
                email.to_addresses
                or []
            ),
            cc_addresses=(
                email.cc_addresses
                or []
            ),
            bcc_addresses=(
                email.bcc_addresses
                or []
            ),
            received_at=(
                email.received_at
            ),
            body_text=(
                email.body_text
            ),
            body_html=(
                email.body_html
            ),
            attachments=(
                email.attachments
                or []
            ),
            parse_warnings=(
                email.parse_warnings
                or []
            ),
            lifecycle=(
                InvestigationLifecycle(
                    status=(
                        lifecycle.status
                    ),
                    latest_analysis_id=(
                        lifecycle
                        .latest_analysis_id
                    ),
                    updated_by=(
                        lifecycle.updated_by
                    ),
                    updated_at=(
                        lifecycle.updated_at
                    ),
                )
            ),
            decision=decision,
            modules=modules,
            analysis_history=(
                analysis_history
            ),
            action_history=(
                action_history
            ),
        )

    @staticmethod
    def _extract_url_count(
        analysis,
    ) -> int:

        if analysis is None:
            return 0

        modules = (
            analysis.module_results
            or []
        )

        for module in modules:

            if (
                module.get("module")
                != "ioc_extraction"
            ):
                continue

            metadata = (
                module.get(
                    "metadata",
                    {},
                )
            )

            return int(
                metadata.get(
                    "url_count",
                    0,
                )
                or 0
            )

        return 0