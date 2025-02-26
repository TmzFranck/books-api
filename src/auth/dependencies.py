from fastapi.security import HTTPBearer
from typing import Optional
from fastapi import HTTPException, status, Request
from .utils import decode_token
from src.database.redis import token_in_blocklist

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool =True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        creds = await super().__call__(request)

        assert creds
        token = creds.credentials
        token_data = decode_token(token)

        assert token_data
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN, detail={
                                "error":"This token is invalid or expired",
                                "resolution":"Please get new token"
                           }
                        )

        if not self.token_valid(token):
            raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN, detail={
                                "error":"This token is invalid or expired",
                                "resolution":"Please get new token"
                            }
                        )

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
                raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Please provide an access token",
                            )

class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, token_data) -> None:
            if token_data and not token_data["refresh"]:
                raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Please provide a refresh token",
                            )
