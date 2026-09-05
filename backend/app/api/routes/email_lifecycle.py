from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User

from app.schemas.email_lifecycle import (
    EmailActionHistoryItem,
    EmailLifecycleResponse,
    LifecycleSummary,
    ManualActionRequest,
)

from app.services.email_lifecycle_service import (
    EmailLifecycleService,
)

from app.services.email_query_service import (
    EmailQueryService,
)


router = APIRouter()


def ensure_email_owner(
    db: Session,
    email_id: UUID,
    user_id: UUID,
) -> None:
    EmailQueryService(
        db
    ).get_for_user(
        email_id=email_id,
        user_id=user_id,
    )


@router.get(
    "/summary",
    response_model=LifecycleSummary,
)
def lifecycle_summary(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return EmailLifecycleService(
        db
    ).get_summary_for_user(
        current_user.id
    )


@router.get(
    "/emails/{email_id}",
    response_model=EmailLifecycleResponse,
)
def get_email_state(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).get_state(
        email_id
    )


@router.get(
    "/emails/{email_id}/history",
    response_model=list[
        EmailActionHistoryItem
    ],
)
def get_email_action_history(
    email_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).get_history(
        email_id
    )


@router.post(
    "/emails/{email_id}/quarantine",
    response_model=EmailLifecycleResponse,
)
def quarantine_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).manual_quarantine(
        email_id=email_id,
        reason=payload.reason,
    )


@router.post(
    "/emails/{email_id}/block",
    response_model=EmailLifecycleResponse,
)
def block_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).manual_block(
        email_id=email_id,
        reason=payload.reason,
    )


@router.post(
    "/emails/{email_id}/review",
    response_model=EmailLifecycleResponse,
)
def review_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).manual_review(
        email_id=email_id,
        reason=payload.reason,
    )


@router.post(
    "/emails/{email_id}/allow",
    response_model=EmailLifecycleResponse,
)
def allow_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).manual_allow(
        email_id=email_id,
        reason=payload.reason,
    )


@router.post(
    "/emails/{email_id}/release",
    response_model=EmailLifecycleResponse,
)
def release_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).release(
        email_id=email_id,
        reason=payload.reason,
    )


@router.post(
    "/emails/{email_id}/restore",
    response_model=EmailLifecycleResponse,
)
def restore_email(
    email_id: UUID,
    payload: ManualActionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    ensure_email_owner(
        db,
        email_id,
        current_user.id,
    )

    return EmailLifecycleService(
        db
    ).restore(
        email_id=email_id,
        reason=payload.reason,
    )