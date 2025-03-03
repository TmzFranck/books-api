import uuid
from datetime import datetime, timedelta
from typing import Union

import jwt
from passlib.context import CryptContext

from src.config import Config

passwd_context = CryptContext(schemes=["bcrypt"])


def generate_password_hash(password: str) -> str:
    hash_password = passwd_context.hash(password)
    return hash_password


def verify_password(password: str, hash_password: str) -> bool:
    return passwd_context.verify(password, hash_password)


def create_access_token(
    user_data: dict, expiry: Union[timedelta, None] = None, refresh: bool = False
) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry else timedelta(minutes=60)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    token = jwt.encode(payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> Union[dict, None]:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except Exception:
        return None
