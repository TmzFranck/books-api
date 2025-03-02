from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.schemas import BookCreateModel, BookModel, BookUpdateModel
from src.books.service import BookService
from src.database.main import get_session

book_router = APIRouter()
book_service = BookService()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[BookModel], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.post(
    "/",
    response_model=BookModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    assert token_details
    user_uid = token_details.get("user", {})["user_uid"]
    new_book = await book_service.create_book(book_data, user_uid, session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookModel, dependencies=[role_checker])
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.patch("/{book_uid}", dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
) -> dict:
    book = await book_service.update_book(book_uid, book_update_data, session)
    if book:
        return book.model_dump()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    book = await book_service.delete_book(book_uid, session)
    if book is not None:
        return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.get(
    "/user/{user_uid}", response_model=List[BookModel], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str, session: AsyncSession = Depends(get_session)
):
    books = await book_service.get_user_books(user_uid, session)

    return books
