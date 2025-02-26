from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
from typing import List
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from src.auth.dependencies import AccessTokenBearer

book_router = APIRouter()
book_service = BookService()

@book_router.get("/books", response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())):
    books = await book_service.get_all_books(session)
    return books


@book_router.post("/books", status_code= status.HTTP_201_CREATED)
async def create_a_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())) -> dict:
    new_book = await book_service.create_book(book_data, session)
    return new_book.model_dump()

@book_router.get("/books/{book_uid}")
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book.model_dump()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.patch("/book/{book_uid}")
async def update_book(book_uid: str, book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())) -> dict:
    book = await book_service.update_book(book_uid, book_update_data, session)
    if book:
        return book.model_dump()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.delete("/book/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())):
    book = await book_service.delete_book(book_uid, session)
    if book is not None:
        return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
