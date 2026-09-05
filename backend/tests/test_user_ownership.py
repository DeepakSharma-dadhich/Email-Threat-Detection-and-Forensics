from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import AppError
from app.services.email_query_service import EmailQueryService
from app.services.mailbox_service import MailboxService


class FakeEmailRepository:
    def __init__(self, records):
        self.records = records

    def get_for_user(
        self,
        email_id,
        user_id,
    ):
        record = self.records.get(email_id)

        if record is None:
            return None

        if record.user_id != user_id:
            return None

        return record

    def list_for_user(
        self,
        user_id,
        limit,
        offset,
    ):
        records = [
            record
            for record in self.records.values()
            if record.user_id == user_id
        ]

        return (
            records[offset:offset + limit],
            len(records),
        )


class FakeMailboxRepository:
    def __init__(
        self,
        email,
    ):
        self.email = email

    def get_email(
        self,
        email_id,
        user_id,
    ):
        if (
            self.email.id == email_id
            and self.email.user_id == user_id
        ):
            return self.email

        return None


def make_email(
    user_id,
    subject,
):
    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        source_type="eml",
        source_message_id=None,
        original_filename="test.eml",
        message_id=f"<{uuid4()}@example.com>",
        subject=subject,
        from_address={
            "name": "Test Sender",
            "address": "sender@example.com",
        },
        reply_to=None,
        return_path="bounce@example.com",
        to_addresses=[
            {
                "name": "Test User",
                "address": "user@example.com",
            }
        ],
        cc_addresses=[],
        bcc_addresses=[],
        received_at=now,
        headers=[],
        body_text="Ownership security test email.",
        body_html=None,
        attachments=[],
        raw_sha256="0" * 64,
        raw_storage_key="tests/test.eml",
        raw_size_bytes=100,
        parse_warnings=[],
        created_at=now,
        updated_at=now,
    )


def test_user_can_access_own_email():
    user_a = uuid4()

    email = make_email(
        user_id=user_a,
        subject="User A Email",
    )

    service = EmailQueryService(
        db=None
    )

    service.repository = FakeEmailRepository(
        {
            email.id: email,
        }
    )

    result = service.get_for_user(
        email_id=email.id,
        user_id=user_a,
    )

    assert result.email_id == email.id
    assert result.subject == "User A Email"


def test_user_cannot_access_other_users_email():
    user_a = uuid4()
    user_b = uuid4()

    email = make_email(
        user_id=user_a,
        subject="Private User A Email",
    )

    service = EmailQueryService(
        db=None
    )

    service.repository = FakeEmailRepository(
        {
            email.id: email,
        }
    )

    with pytest.raises(AppError) as exc:
        service.get_for_user(
            email_id=email.id,
            user_id=user_b,
        )

    assert exc.value.status_code == 404


def test_user_email_lists_are_isolated():
    user_a = uuid4()
    user_b = uuid4()

    email_a1 = make_email(
        user_a,
        "User A Email 1",
    )

    email_a2 = make_email(
        user_a,
        "User A Email 2",
    )

    email_b1 = make_email(
        user_b,
        "User B Email 1",
    )

    repository = FakeEmailRepository(
        {
            email_a1.id: email_a1,
            email_a2.id: email_a2,
            email_b1.id: email_b1,
        }
    )

    service = EmailQueryService(
        db=None
    )

    service.repository = repository

    user_a_result = service.list_for_user(
        user_id=user_a,
        limit=20,
        offset=0,
    )

    user_b_result = service.list_for_user(
        user_id=user_b,
        limit=20,
        offset=0,
    )

    assert user_a_result.total == 2
    assert user_b_result.total == 1

    user_a_ids = {
        item.email_id
        for item in user_a_result.items
    }

    user_b_ids = {
        item.email_id
        for item in user_b_result.items
    }

    assert email_a1.id in user_a_ids
    assert email_a2.id in user_a_ids
    assert email_b1.id not in user_a_ids

    assert email_b1.id in user_b_ids
    assert email_a1.id not in user_b_ids
    assert email_a2.id not in user_b_ids


def test_mailbox_investigation_hides_foreign_email():
    user_a = uuid4()
    user_b = uuid4()

    email = make_email(
        user_a,
        "User A Investigation",
    )

    service = MailboxService(
        db=None
    )

    service.repository = FakeMailboxRepository(
        email=email
    )

    with pytest.raises(Exception) as exc:
        service.get_investigation(
            email_id=email.id,
            user_id=user_b,
        )

    error = exc.value

    assert getattr(
        error,
        "status_code",
        None,
    ) == 404


def test_mailbox_owner_passes_first_security_check():
    user_a = uuid4()

    email = make_email(
        user_a,
        "Owned Investigation",
    )

    repository = FakeMailboxRepository(
        email=email
    )

    result = repository.get_email(
        email_id=email.id,
        user_id=user_a,
    )

    assert result is not None
    assert result.user_id == user_a


def test_different_users_have_different_gmail_token_paths(
    tmp_path,
    monkeypatch,
):
    from app.core.config import settings
    from app.integrations.gmail_auth import GmailAuthClient

    user_a = uuid4()
    user_b = uuid4()

    monkeypatch.setattr(
        settings,
        "storage_root",
        tmp_path,
    )

    client_a = GmailAuthClient(
        user_id=user_a
    )

    client_b = GmailAuthClient(
        user_id=user_b
    )

    assert client_a.token_path != client_b.token_path

    assert str(user_a) in str(
        client_a.token_path
    )

    assert str(user_b) in str(
        client_b.token_path
    )


def test_user_b_does_not_detect_user_a_gmail_token(
    tmp_path,
    monkeypatch,
):
    from app.core.config import settings
    from app.integrations.gmail_auth import GmailAuthClient

    user_a = uuid4()
    user_b = uuid4()

    monkeypatch.setattr(
        settings,
        "storage_root",
        tmp_path,
    )

    client_a = GmailAuthClient(
        user_id=user_a
    )

    client_b = GmailAuthClient(
        user_id=user_b
    )

    client_a.token_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    client_a.token_path.write_text(
        "{}",
        encoding="utf-8",
    )

    assert client_a.has_token() is True
    assert client_b.has_token() is False