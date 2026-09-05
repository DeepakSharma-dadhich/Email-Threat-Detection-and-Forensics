from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from app.analysis.orchestrator import (
    AnalysisOrchestrator,
)

from app.schemas.email import (
    CommonEmailObject,
    Mailbox,
    RawArtifactInfo,
    SourceInfo,
)


def test_orchestrator_returns_four_module_results():

    now = datetime.now(
        timezone.utc
    )

    email = CommonEmailObject(

        email_id=uuid4(),

        source=SourceInfo(
            type="eml"
        ),

        subject="Hello",

        from_address=Mailbox(
            address="a@example.com"
        ),

        to=[
            Mailbox(
                address="b@example.com"
            )
        ],

        body_text=(
            "Visit "
            "https://example.com"
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
        AnalysisOrchestrator()
        .analyze(email)
    )

    assert (
        len(
            result.module_results
        )
        == 4
    )

    assert (
        result.aggregate_score
        is None
    )