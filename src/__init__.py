from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.database.main import initdb
from src.errors import register_error_handlers
from src.reviews.routes import review_router
from src.tags.routes import tags_router

from .middleware import register_middleware

version = "v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initdb()
    yield
    print("server is stopping")


app = FastAPI(
    title="Books API",
    description="A RESTful API for a book review web service",
    version=version,
)

register_error_handlers(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
