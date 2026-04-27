import os

import psycopg2
from dotenv import load_dotenv

from repositories.book_repository import BookRepository
from repositories.postgresql_book_repository import PostgreSQLBookRepository

load_dotenv()


def provide_book_repository() -> BookRepository:
    database_url = os.getenv("DATABASE_URL")
    sslmode = os.getenv("DB_SSLMODE", "prefer")
    if database_url:
        connection = psycopg2.connect(database_url, sslmode=sslmode)
    else:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=os.getenv("DB_NAME", "lab2_books"),
            sslmode=sslmode,
        )
    return PostgreSQLBookRepository(connection=connection)
