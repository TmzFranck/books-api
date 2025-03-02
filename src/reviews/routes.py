from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_active_user
from src.database.main import get_session
from src.database.models import User

from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService

review_service = ReviewService()
review_router = APIRouter()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get(
    "/", response_model=List[ReviewModel], dependencies=[user_role_checker]
)
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session)

    return reviews


@review_router.get(
    "/{review_uid}", response_model=ReviewModel, dependencies=[user_role_checker]
)
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await review_service.get_review(review_uid, session)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@review_router.post(
    "/book/{book_uid}", response_model=ReviewModel, dependencies=[user_role_checker]
)
async def create_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    new_review = await review_service.add_review_to_book(
        current_user.email, book_uid, review_data, session
    )

    return new_review


@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review_to_form_book(
        review_uid, current_user.email, session
    )

    return None
