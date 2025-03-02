from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.database.models import Tag
from src.errors import (
    BookNotFoundError,
    TagAlreadyExistsError,
    TagNotFoundError,
)

from .schemas import TagAddModel, TagCreateModel

book_service = BookService()


class TagService:
    async def get_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.exec(statement)

        return result.all()

    async def add_tag_to_book(
        self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
    ):
        book = await book_service.get_book(book_uid, session)

        if not book:
            raise BookNotFoundError()

        for tag_item in tag_data.tags:
            statement = select(Tag).where(Tag.name == tag_item.name)

            result = await session.exec(statement)

            tag = result.one_or_none()

            if not tag:
                tag = Tag(**tag_data.model_dump())

            book.tags.append(tag)
            await session.commit()
            await session.refresh(book)
            return book

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.exec(statement)

        return result.first()

    async def create_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_data.name)

        result = await session.exec(statement)

        tag = result.first()

        if tag:
            raise TagAlreadyExistsError()

        new_tag = Tag(**tag_data.model_dump())

        session.add(new_tag)
        await session.commit()
        return new_tag

    async def update_tag(
        self, tag_uid: str, tag_data: TagCreateModel, session: AsyncSession
    ):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFoundError

        update_tag_data_dict = tag_data.model_dump()

        for key, value in update_tag_data_dict.items():
            setattr(tag, key, value)

            await session.commit()
            await session.refresh(tag)

        return tag

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFoundError

        await session.delete(tag)
        await session.commit()
