#
# ?FastApi
from fastapi import FastAPI, Request


# ?Third Party packages
import databases  # Databases gives you simple asyncio support for a range of databases.
import sqlalchemy  # A powerful and popular Object-Relational Mapping (ORM) library that supports multiple database backends, including PostgreSQL, MySQL, SQLite, and more.
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
print("Database url is ", DATABASE_URL)
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
)
# Create Postgress Engine
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


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
    print("Query", query)
    return await database.fetch_all(query)


#!create_book
@app.post("/books/")
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"last_record_id": last_record_id}
