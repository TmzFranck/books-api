from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class BookError(Exception): ...


class InvalidTokenError(BookError): ...


class RevokedTokenError(InvalidTokenError): ...


class AccessTokenError(InvalidTokenError): ...


class RefreshTokenError(InvalidTokenError): ...


class UserAlreadyExistsError(BookError): ...


class InvalidCredentialsError(BookError): ...


class InsufficientPermissionsError(BookError): ...


class BookNotFoundError(BookError): ...


class TagNotFoundError(BookError): ...


class TagAlreadyExistsError(BookError): ...


class UserNotFoundError(BookError): ...


class ReviewNotFoundError(BookError): ...


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=status_code, content=initial_detail)

    return exception_handler


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExistsError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "User_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentialsError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an new refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermissionsError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get new token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExistsError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Tag already exists",
                "error_code": "tag_already_exists",
            },
        ),
    )

    app.add_exception_handler(
        TagNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "tag_not_found",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ReviewNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Review not found",
                "error_code": "review_not_found",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Oops! Something went wrong",
                "error_code": "internal_server_error",
            },
        )
