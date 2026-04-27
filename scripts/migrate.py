import os
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as PgConnection


def _connect() -> PgConnection:
    database_url = os.getenv("DATABASE_URL")
    sslmode = os.getenv("DB_SSLMODE", "prefer")
    if database_url:
        return psycopg2.connect(database_url, sslmode=sslmode)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        dbname=os.getenv("DB_NAME", "lab2_books"),
        sslmode=sslmode,
    )


def _apply_sql_file(connection: PgConnection, file_path: Path) -> None:
    sql = file_path.read_text(encoding="utf-8")
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()


def _has_column(connection: PgConnection, table_name: str, column_name: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = %s
          AND column_name = %s
        """,
        (table_name, column_name),
    )
    row = cursor.fetchone()[0]
    cursor.close()
    return bool(row)


def _books_count(connection: PgConnection) -> int:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    row = cursor.fetchone()[0]
    cursor.close()
    return int(row)


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
