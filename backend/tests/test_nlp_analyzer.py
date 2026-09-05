from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from app.analysis.nlp.analyzer import (
    NLPAnalyzer,
)

from app.schemas.email import (
    CommonEmailObject,
    Mailbox,
    RawArtifactInfo,
    SourceInfo,
)


def test_nlp_detects_credential_and_urgency_language():

    now = datetime.now(
        timezone.utc
    )

    email = CommonEmailObject(

        email_id=uuid4(),

        source=SourceInfo(
            type="eml"
        ),

        subject=(
            "Urgent: verify your account"
        ),

        from_address=Mailbox(
            address="a@example.com"
        ),

        to=[
            Mailbox(
                address="b@example.com"
            )
        ],

        body_text=(
            "Act now. Click here and "
            "enter your password to "
            "verify your account."
        ),

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

    result = (
        NLPAnalyzer()
        .analyze(email)
    )

    assert result.score > 0

    assert (
        result.metadata[
            "category_count"
        ]
        >= 2
    )