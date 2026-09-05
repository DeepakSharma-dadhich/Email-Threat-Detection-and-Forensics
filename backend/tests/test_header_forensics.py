from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from app.analysis.header_forensics.analyzer import (
    HeaderForensicsAnalyzer,
)

from app.schemas.email import (
    CommonEmailObject,
    HeaderItem,
    Mailbox,
    RawArtifactInfo,
    SourceInfo,
)


def build_email():

    now = datetime.now(
        timezone.utc
    )

    return CommonEmailObject(

        email_id=uuid4(),

        source=SourceInfo(
            type="eml"
        ),

        message_id=(
            "<x@sender.com>"
        ),

        subject="hello",

        from_address=Mailbox(
            name="A",
            address="a@sender.com",
        ),

        reply_to=Mailbox(
            address="reply@other.com"
        ),

        return_path=(
            "<bounce@other.com>"
        ),

        to=[
            Mailbox(
                address="b@example.com"
            )
        ],

        headers=[

            HeaderItem(
                name="Date",
                value=(
                    "Wed, 02 Sep 2026 "
                    "10:00:00 +0530"
                ),
            ),

            HeaderItem(
                name=(
                    "Authentication-Results"
                ),
                value=(
                    "mx; "
                    "spf=fail "
                    "dkim=pass "
                    "dmarc=fail"
                ),
            ),
        ],

        raw_artifact=(
            RawArtifactInfo(
                sha256="0" * 64,
                size_bytes=10,
                storage_key="x",
            )
        ),

        created_at=now,

        updated_at=now,
    )


def test_header_analyzer_flags_alignment_and_authentication():

    result = (
        HeaderForensicsAnalyzer()
        .analyze(
            build_email()
        )
    )

    assert result.score > 0

    assert any(
        "Reply-To"
        in finding.title

        for finding
        in result.findings
    )