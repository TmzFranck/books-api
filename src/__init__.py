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
version_prefix ="/api/{version}"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initdb()
    yield
    print("server is stopping")


app = FastAPI(
    title="Books API",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
            "name": "Franck Boudouin Tameze",
            "url": "https://github.com/TmzFranck",
            "email": "francktameze5@gmail.com",
        },
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_error_handlers(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/{version_prefix}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/{version_prefix}/tags", tags=["tags"])
