from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.core.config import settings


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailAuthClient:
    def __init__(self):
        self.credentials_path = Path(
            settings.GMAIL_CREDENTIALS_PATH
        )

        self.token_path = Path(
            settings.GMAIL_TOKEN_PATH
        )

    def get_credentials(self) -> Credentials:
        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path),
                GMAIL_SCOPES,
            )

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        elif credentials is None or not credentials.valid:
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    "Gmail OAuth credentials file not found at "
                    f"{self.credentials_path}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                GMAIL_SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        self.token_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.token_path.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

        return credentials

    def build_service(self):
        credentials = self.get_credentials()

        return build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )