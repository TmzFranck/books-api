from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker
from src.books.schemas import BookModel
from src.database.main import get_session

from .schemas import TagAddModel, TagCreateModel, TagModel
from .service import TagService

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tags_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_tags(session)

    return tags


@tags_router.post(
    "/",
    response_model=TagModel,
    dependencies=[user_role_checker],
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(tag: TagCreateModel, session: AsyncSession = Depends(get_session)):
    tag_added = await tag_service.create_tag(tag, session)

    return tag_added


@tags_router.post(
    "/book/{book_uid}/tags", response_model=BookModel, dependencies=[user_role_checker]
)
async def add_tag_to_book(
    tag_data: TagAddModel, book_uid: str, session: AsyncSession = Depends(get_session)
):
    book_with_tag = await tag_service.add_tag_to_book(book_uid, tag_data, session)

    return book_with_tag


@tags_router.put(
    "/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker]
)
async def update_tag(
    tag_uid: str, tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    tag_updated = await tag_service.update_tag(tag_uid, tag_data, session)

    return tag_updated


@tags_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)):
    await tag_service.delete_tag(tag_uid, session)
