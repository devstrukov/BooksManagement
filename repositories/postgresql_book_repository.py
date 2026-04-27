from __future__ import annotations

from typing import Optional

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from domain.book_dto import BookDTO
from repositories.book_repository import BookRepository


class PostgreSQLBookRepository(BookRepository):
    def __init__(self, connection: PgConnection) -> None:
        self._connection = connection

    def get_book_by_id(self, book_id: int) -> Optional[BookDTO]:
        query = """
            SELECT
                b.id,
                b.title,
                b.description,
                b.link,
                b.author,
                b.price,
                b.pages,
                b.rating,
                b.created_at,
                b.updated_at
            FROM books b
            WHERE b.id = %s
            LIMIT 1
        """

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (book_id,))
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None

        return BookDTO(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            link=row["link"],
            author=row["author"],
            price=float(row["price"]),
            pages=int(row["pages"]),
            rating=float(row["rating"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_books(self, sort_by: str, order: str) -> list[BookDTO]:
        query = f"""
            SELECT
                b.id,
                b.title,
                b.description,
                b.link,
                b.author,
                b.price,
                b.pages,
                b.rating,
                b.created_at,
                b.updated_at
            FROM books b
            ORDER BY b.{sort_by} {order}
        """

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return [
            BookDTO(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                link=row["link"],
                author=row["author"],
                price=float(row["price"]),
                pages=int(row["pages"]),
                rating=float(row["rating"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def create_book(
        self,
        title: str,
        description: str,
        link: str,
        author: str,
        price: float,
        pages: int,
        rating: float,
    ) -> BookDTO:
        query = """
            INSERT INTO books (title, description, link, author, price, pages, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        cursor = self._connection.cursor()
        cursor.execute(query, (title, description, link, author, price, pages, rating))
        new_id = cursor.fetchone()[0]
        self._connection.commit()
        cursor.close()
        return self.get_book_by_id(new_id)

    def update_book(
        self,
        book_id: int,
        title: str,
        description: str,
        link: str,
        author: str,
        price: float,
        pages: int,
        rating: float,
    ) -> Optional[BookDTO]:
        query = """
            UPDATE books
            SET title = %s,
                description = %s,
                link = %s,
                author = %s,
                price = %s,
                pages = %s,
                rating = %s,
                updated_at = NOW()
            WHERE id = %s
        """

        cursor = self._connection.cursor()
        cursor.execute(query, (title, description, link, author, price, pages, rating, book_id))
        updated_rows = cursor.rowcount
        self._connection.commit()
        cursor.close()

        if updated_rows == 0:
            return None
        return self.get_book_by_id(book_id)

    def delete_book(self, book_id: int) -> bool:
        query = "DELETE FROM books WHERE id = %s"
        cursor = self._connection.cursor()
        cursor.execute(query, (book_id,))
        deleted_rows = cursor.rowcount
        self._connection.commit()
        cursor.close()
        return deleted_rows > 0

    def get_id_stats(self) -> dict[str, float | int | None]:
        query = """
            SELECT
                COUNT(*) AS total_count,
                MIN(price) AS min_price,
                MAX(price) AS max_price,
                AVG(price) AS avg_price,
                MIN(pages) AS min_pages,
                MAX(pages) AS max_pages,
                AVG(pages) AS avg_pages,
                MIN(rating) AS min_rating,
                MAX(rating) AS max_rating,
                AVG(rating) AS avg_rating
            FROM books
        """

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()

        return {
            "total_count": row["total_count"],
            "min_price": float(row["min_price"]) if row["min_price"] is not None else None,
            "max_price": float(row["max_price"]) if row["max_price"] is not None else None,
            "avg_price": float(row["avg_price"]) if row["avg_price"] is not None else None,
            "min_pages": int(row["min_pages"]) if row["min_pages"] is not None else None,
            "max_pages": int(row["max_pages"]) if row["max_pages"] is not None else None,
            "avg_pages": float(row["avg_pages"]) if row["avg_pages"] is not None else None,
            "min_rating": float(row["min_rating"]) if row["min_rating"] is not None else None,
            "max_rating": float(row["max_rating"]) if row["max_rating"] is not None else None,
            "avg_rating": float(row["avg_rating"]) if row["avg_rating"] is not None else None,
        }
