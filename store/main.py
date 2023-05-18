#
# ?FastApi
from fastapi import FastAPI, Request


# ?Third Party packages
import databases  # Databases gives you simple asyncio support for a range of databases.
import sqlalchemy  # A powerful and popular Object-Relational Mapping (ORM) library that supports multiple database backends, including PostgreSQL, MySQL, SQLite, and more.
from sqlalchemy import select
from decouple import config


# Postgress Settings
POSTGRES_HOST = config("POSTGRES_HOST")
POSTGRES_DB = config("POSTGRES_DB")
POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_PORT = config("POSTGRES_PORT", 5432)


# Database Url
DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
)
database = databases.Database(DATABASE_URL)


# Sqlalchemy and Tables
metadata = sqlalchemy.MetaData()

# *Books
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
    sqlalchemy.Column("pages", sqlalchemy.Integer),
)

# *Readers
readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
)

# *Readers Books
readers_books = sqlalchemy.Table(
    "readers_books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("book", sqlalchemy.ForeignKey("books.id"), nullable=False),
    sqlalchemy.Column("readers", sqlalchemy.ForeignKey("readers.id"), nullable=False),
)


# NOTE => If you have integrate Alembic to your project,don't need this code block create table on Database
"""
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
"""


# Create FastApi Object and Define Api Endpoint
app = FastAPI()


#!startup
# When open localhost,work this view automatically and close database connection
@app.on_event("startup")
async def startup():
    print("Start server successfully")
    await database.connect()


#!shutdown
# When closed port,work this view automatically and close database connection
@app.on_event("shutdown")
async def shutdown():
    print("Close server successfully")
    await database.disconnect()


#!get_all_books
@app.get("/books/")
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)


#!create_book
@app.post("/books/")
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    book_id = await database.execute(query)
    return {"book_id": book_id}


#!create_reader
@app.post("/readers/")
async def create_reader(request: Request):
    data = await request.json()
    query = readers.insert().values(**data)
    reader_id = await database.execute(query)
    return {"reader_id": reader_id}


#!read_book
@app.post("/read/")
async def read_book(request: Request):
    data = await request.json()
    query = readers_books.insert().values(**data)
    reader_book_id = await database.execute(query)
    return {"readers_book_id": reader_book_id}


#!get_reader_books
@app.get("/reader/books/{reader_id}/")
async def get_reader_books(request: Request, reader_id: int):
    query = readers_books.select().where(readers_books.c.readers == reader_id)
    reader_books = await database.fetch_all(query)
    return reader_books
