from app.integrations.gmail_auth import GmailAuthClient
from app.schemas.gmail import (
    GmailConnectionResponse,
    GmailMessageListResponse,
    GmailMessageSummary,
)


class GmailService:
    def __init__(self):
        auth_client = GmailAuthClient()
        self.gmail_api = auth_client.build_service()

    def connection_status(
        self,
    ) -> GmailConnectionResponse:
        profile = (
            self.gmail_api
            .users()
            .getProfile(userId="me")
            .execute()
        )

        return GmailConnectionResponse(
            connected=True,
            email_address=profile.get(
                "emailAddress"
            ),
        )

    def list_messages(
        self,
        limit: int = 10,
    ) -> GmailMessageListResponse:
        response = (
            self.gmail_api
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
                self.gmail_api
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
                    gmail_message_id=message["id"],
                    gmail_thread_id=message.get(
                        "threadId"
                    ),
                    label_ids=message.get(
                        "labelIds",
                        [],
                    ),
                )
            )

        return GmailMessageListResponse(
            count=len(messages),
            messages=messages,
        )