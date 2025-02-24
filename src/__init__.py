from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.database.main import initdb

version = "v1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initdb()
    yield
    print("server is stopping")

app = FastAPI(
    lifespan=lifespan,
    title="Books API",
    description="A RESTful API for a book review web service",
     version=version,
)

app.include_router(book_router, prefix=f"/api/{version}", tags=["books"])
