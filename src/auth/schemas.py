import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field

from src.books.schemas import BookModel


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    is_verified: bool = False
    email: EmailStr
    password_hash: str
    created_at: datetime
    updated_at: datetime


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)


class UserLoginModel(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)


class UserBooksModel(UserModel):
    books: List[BookModel]


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: EmailStr


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
