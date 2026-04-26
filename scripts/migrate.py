import os
from pathlib import Path

import mysql.connector
from mysql.connector.connection import MySQLConnection


def _connect() -> MySQLConnection:
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "lab2_books"),
    )


def _apply_sql_file(connection: MySQLConnection, file_path: Path) -> None:
    sql = file_path.read_text(encoding="utf-8")
    cursor = connection.cursor()
    for _ in cursor.execute(sql, multi=True):
        pass
    connection.commit()
    cursor.close()


def _has_column(connection: MySQLConnection, table_name: str, column_name: str) -> bool:
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
        """,
        (table_name, column_name),
    )
    row = cursor.fetchone()
    cursor.close()
    return bool(row["total"])


def _books_count(connection: MySQLConnection) -> int:
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM books")
    row = cursor.fetchone()
    cursor.close()
    return int(row["total"])


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    migration_001 = root / "migrations" / "001_create_tables.sql"
    migration_002 = root / "migrations" / "002_add_book_numeric_fields.sql"
    migration_003 = root / "migrations" / "003_seed_books.sql"

    connection = _connect()
    try:
        _apply_sql_file(connection, migration_001)

        if not _has_column(connection, "books", "price"):
            _apply_sql_file(connection, migration_002)

        if _books_count(connection) == 0:
            _apply_sql_file(connection, migration_003)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
