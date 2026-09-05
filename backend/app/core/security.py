from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from jwt import InvalidTokenError

from app.core.config import settings


def hash_password(
    password: str,
) -> str:

    password_bytes = password.encode(
        "utf-8"
    )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    except ValueError:
        return False


def create_access_token(
    user_id: UUID,
    email: str,
) -> tuple[str, int]:

    expires_delta = timedelta(
        minutes=(
            settings
            .access_token_expire_minutes
        )
    )

    now = datetime.now(
        timezone.utc
    )

    expires_at = (
        now
        + expires_delta
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=(
            settings.jwt_algorithm
        ),
    )

    return (
        token,
        int(
            expires_delta.total_seconds()
        ),
    )


def decode_access_token(
    token: str,
) -> dict:

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[
            settings.jwt_algorithm
        ],
    )

    if (
        payload.get("type")
        != "access"
    ):
        raise InvalidTokenError(
            "Invalid token type."
        )

    return payload