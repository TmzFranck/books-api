from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Book
from src.books.schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from datetime import datetime
import uuid

class BookService:

    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d").date()

        session.add(new_book)

        await session.commit()

        return new_book

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == uuid.UUID(book_uid))

        result = await session.exec(statement)

        book = result.first()

        return book if book else None

    async def update_book(self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update:
            update_data_dict = update_data.model_dump()

            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)

            setattr(book_to_update, "updated_at", datetime.now())

            await session.commit()

            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
