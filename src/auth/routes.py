from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from src.database.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import verify_password, create_access_token
from datetime import timedelta
from fastapi.responses import JSONResponse
from .dependencies import (RefreshTokenBearer, AccessTokenBearer, get_current_active_user)
from datetime import datetime
from src.database.redis import add_jti_to_block_list
from .schemas import UserBooksModel
from .dependencies import RoleChecker

auth_router = APIRouter()
user_service = UserService()
refresh_token_service = RefreshTokenBearer()
role_checker = RoleChecker(["admin"])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists")
    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post("/login")
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user:
        password_is_valid = verify_password(password, user.password_hash)

        if password_is_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)})

            refresh_token = create_access_token(
                            user_data={"email": user.email, "user_uid": str(user.uid)},
                            refresh=True,
                            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                        )
            return JSONResponse(
                    content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                            })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Email or Password")

@auth_router.post("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_service)):

    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            new_access_token = create_access_token(user_data=token_details["user"])

            return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Or expired token"
        )

@auth_router.post("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]

    await add_jti_to_block_list(jti)

    return JSONResponse(
        content={"message": "Logout successful"},
        status_code=status.HTTP_200_OK)

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(user=Depends(get_current_active_user), _:bool = Depends(role_checker)) -> UserBooksModel:
    return user
