from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from src.config import Config
import uuid
import logging
from typing import Union

passwd_context = CryptContext(
    schemes=['bcrypt']
)

def generate_password_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)

def create_access_token(user_data: dict, expiry: Union[timedelta, None] = None, refresh: bool = False) -> str:
    payload = {
        'user': user_data,
        'exp': datetime.now() + (expiry if expiry else timedelta(minutes=60)),
        'jti': str(uuid.uuid4()),
        'refresh': refresh
    }

    token = jwt.encode(payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> Union[dict, None]:
    try:
        token_data = jwt.decode(jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM])
        return token_data
    except jwt.PyJWTError as jwt_error:
        logging.exception(jwt_error)
        return None
    except Exception as e:
        logging.exception(e)
        return None
