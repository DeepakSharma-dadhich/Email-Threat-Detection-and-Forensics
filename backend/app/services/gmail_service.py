from uuid import UUID

from app.integrations.gmail_auth import (
    GmailAuthClient,
)
from app.schemas.gmail import (
    GmailConnectionResponse,
    GmailMessageListResponse,
    GmailMessageSummary,
)


class GmailService:
    def __init__(
        self,
        user_id: UUID,
    ):
        self.user_id = user_id
        self.auth_client = (
            GmailAuthClient(
                user_id=user_id
            )
        )

    def connection_status(
        self,
    ) -> GmailConnectionResponse:

        if not self.auth_client.has_token():
            return GmailConnectionResponse(
                connected=False,
                email_address=None,
            )

        try:
            gmail_api = (
                self.auth_client
                .build_service()
            )

            profile = (
                gmail_api
                .users()
                .getProfile(
                    userId="me"
                )
                .execute()
            )

            return GmailConnectionResponse(
                connected=True,
                email_address=(
                    profile.get(
                        "emailAddress"
                    )
                ),
            )

        except Exception:
            return GmailConnectionResponse(
                connected=False,
                email_address=None,
            )

    def list_messages(
        self,
        limit: int = 10,
    ) -> GmailMessageListResponse:

        gmail_api = (
            self.auth_client
            .build_service()
        )

        response = (
            gmail_api
            .users()
            .messages()
            .list(
                userId="me",
                maxResults=limit,
            )
            .execute()
        )

        message_refs = response.get(
            "messages",
            [],
        )

        messages = []

        for item in message_refs:
            message = (
                gmail_api
                .users()
                .messages()
                .get(
                    userId="me",
                    id=item["id"],
                    format="metadata",
                )
                .execute()
            )

            messages.append(
                GmailMessageSummary(
                    gmail_message_id=(
                        message["id"]
                    ),
                    gmail_thread_id=(
                        message.get(
                            "threadId"
                        )
                    ),
                    label_ids=(
                        message.get(
                            "labelIds",
                            [],
                        )
                    ),
                )
            )

        return GmailMessageListResponse(
            count=len(messages),
            messages=messages,
        )