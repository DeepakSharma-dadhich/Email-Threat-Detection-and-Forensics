from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import (
    decode_access_token,
)

from app.db.session import get_db

from app.models.user import User

from app.repositories.user_repository import (
    UserRepository,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_user(
    credentials:
        HTTPAuthorizationCredentials
        | None = Depends(
            bearer_scheme
        ),
    db: Session = Depends(
        get_db
    ),
) -> User:

    unauthorized = HTTPException(
        status_code=401,
        detail=(
            "Authentication required."
        ),
        headers={
            "WWW-Authenticate":
            "Bearer"
        },
    )

    if credentials is None:
        raise unauthorized

    if (
        credentials.scheme.lower()
        != "bearer"
    ):
        raise unauthorized

    try:
        payload = (
            decode_access_token(
                credentials.credentials
            )
        )

        subject = payload.get(
            "sub"
        )

        if subject is None:
            raise unauthorized

        user_id = UUID(
            subject
        )

    except (
        InvalidTokenError,
        ValueError,
    ):
        raise unauthorized

    repository = UserRepository(
        db
    )

    user = repository.get_by_id(
        user_id
    )

    if user is None:
        raise unauthorized

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail=(
                "User account is disabled."
            ),
        )

    return user