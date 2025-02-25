from pydantic import BaseModel, Field, EmailStr
import uuid
from datetime import datetime

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    is_verified: bool = False
    email: EmailStr
    password_hash: str
    created_at: datetime

class UserCreateModel(BaseModel):
    first_name: str =Field(max_length=25)
    last_name:  str =Field(max_length=25)
    username: str = Field(max_length=8)
    email: EmailStr = Field(max_length=40)
    password: str  = Field(min_length=6)
