from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.repositories.user_repository import (
    UserRepository,
)

from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
)


class AuthService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.repository = (
            UserRepository(db)
        )

    def signup(
        self,
        request: SignupRequest,
    ) -> TokenResponse:

        email = str(
            request.email
        ).strip().lower()

        name = (
            request.name.strip()
        )

        if not name:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Name cannot be empty."
                ),
            )

        existing = (
            self.repository
            .get_by_email(email)
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An account with this "
                    "email already exists."
                ),
            )

        password_hash = (
            hash_password(
                request.password
            )
        )

        try:
            user = (
                self.repository.create(
                    name=name,
                    email=email,
                    password_hash=(
                        password_hash
                    ),
                )
            )

        except IntegrityError:
            self.db.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "An account with this "
                    "email already exists."
                ),
            )

        token, expires_in = (
            create_access_token(
                user_id=user.id,
                email=user.email,
            )
        )

        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=user,
        )

    def login(
        self,
        request: LoginRequest,
    ) -> TokenResponse:

        email = str(
            request.email
        ).strip().lower()

        user = (
            self.repository
            .get_by_email(email)
        )

        invalid_credentials = (
            HTTPException(
                status_code=401,
                detail=(
                    "Invalid email or password."
                ),
                headers={
                    "WWW-Authenticate":
                    "Bearer"
                },
            )
        )

        if user is None:
            raise invalid_credentials

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise invalid_credentials

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail=(
                    "User account is disabled."
                ),
            )

        token, expires_in = (
            create_access_token(
                user_id=user.id,
                email=user.email,
            )
        )

        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=user,
        )