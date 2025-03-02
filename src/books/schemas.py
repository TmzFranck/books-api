import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel


class BookModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    reviews: List[ReviewModel]
    tags: List[TagModel]


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    language: str


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
