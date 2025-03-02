from typing import List, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.main import get_session
from src.database.models import User
from src.database.redis import token_in_blocklist
from src.errors import (
    AccessTokenError,
    InsufficientPermissionsError,
    InvalidTokenError,
    RefreshTokenError,
    UserNotFoundError,
)

from .service import UserService
from .utils import decode_token

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        creds = await super().__call__(request)

        assert creds
        token = creds.credentials
        token_data = decode_token(token)

        assert token_data
        if await token_in_blocklist(token_data["jti"]):
            raise InvalidTokenError()

        if not self.token_valid(token):
            raise InvalidTokenError()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenError()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenError()


async def get_current_active_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    user_email = token_details.get("user", {})["email"]

    user = await user_service.get_user_by_email(user_email, session)

    if user:
        return user
    raise UserNotFoundError()


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> bool:
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermissionsError()
