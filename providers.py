import os

import mysql.connector
from dotenv import load_dotenv

from repositories.book_repository import BookRepository
from repositories.mariadb_book_repository import MariaDBBookRepository

load_dotenv()


def provide_book_repository() -> BookRepository:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "lab2_books"),
    )
    return MariaDBBookRepository(connection=connection)
