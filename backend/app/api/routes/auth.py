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

from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
)

from app.services.auth_service import (
    AuthService,
)


router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=201,
)
def signup(
    request: SignupRequest,
    db: Session = Depends(
        get_db
    ),
):
    service = AuthService(db)

    return service.signup(
        request
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(
        get_db
    ),
):
    service = AuthService(db)

    return service.login(
        request
    )


@router.get(
    "/me",
    response_model=(
        CurrentUserResponse
    ),
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user