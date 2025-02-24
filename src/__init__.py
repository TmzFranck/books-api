from fastapi import FastAPI
from src.books.routes import book_router

version = "v1"


app = FastAPI(
    title="Books API",
    description="A RESTful API for a book review web service",
     version=version,
)

app.include_router(book_router, prefix=f"/api/{version}", tags=["books"])
