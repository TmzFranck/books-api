from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.database.models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash
from pydantic import EmailStr

class UserService:

    async def get_user_by_email(self, email: EmailStr, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        return result.first()

    async def user_exists(self, email: str, session : AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_password_hash(user_data_dict["password"])

        session.add(new_user)

        await session.commit()

        return new_user
