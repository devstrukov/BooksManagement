from __future__ import annotations

from datetime import datetime

import pytest

from app import create_app
from domain.book_dto import BookDTO
from repositories.book_repository import BookRepository
from services.book_service import BookService


class InMemoryBookRepository(BookRepository):
    def __init__(self) -> None:
        self._books: dict[int, BookDTO] = {}
        self._next_id = 1

    def get_book_by_id(self, book_id: int) -> BookDTO | None:
        return self._books.get(book_id)

    def list_books(self, sort_by: str, order: str) -> list[BookDTO]:
        reverse = order.upper() == "DESC"
        return sorted(self._books.values(), key=lambda b: getattr(b, sort_by), reverse=reverse)

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
        now = datetime.utcnow()
        book = BookDTO(
            id=self._next_id,
            title=title,
            description=description,
            link=link,
            author=author,
            price=price,
            pages=pages,
            rating=rating,
            created_at=now,
            updated_at=now,
        )
        self._books[self._next_id] = book
        self._next_id += 1
        return book

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
    ) -> BookDTO | None:
        current = self._books.get(book_id)
        if current is None:
            return None

        updated = BookDTO(
            id=current.id,
            title=title,
            description=description,
            link=link,
            author=author,
            price=price,
            pages=pages,
            rating=rating,
            created_at=current.created_at,
            updated_at=datetime.utcnow(),
        )
        self._books[book_id] = updated
        return updated

    def delete_book(self, book_id: int) -> bool:
        if book_id not in self._books:
            return False
        del self._books[book_id]
        return True

    def get_id_stats(self) -> dict[str, float | int | None]:
        if not self._books:
            return {
                "total_count": 0,
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "min_pages": None,
                "max_pages": None,
                "avg_pages": None,
                "min_rating": None,
                "max_rating": None,
                "avg_rating": None,
            }
        prices = [book.price for book in self._books.values()]
        pages = [book.pages for book in self._books.values()]
        ratings = [book.rating for book in self._books.values()]
        return {
            "total_count": len(self._books),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "min_pages": min(pages),
            "max_pages": max(pages),
            "avg_pages": sum(pages) / len(pages),
            "min_rating": min(ratings),
            "max_rating": max(ratings),
            "avg_rating": sum(ratings) / len(ratings),
        }


@pytest.fixture
def client():
    repository = InMemoryBookRepository()
    app = create_app(BookService(repository))
    app.config["TESTING"] = True
    return app.test_client()


def test_create_book_validation_error(client):
    response = client.post(
        "/books",
        json={
            "title": "Book title",
            "description": "desc",
            "author": "Author name",
            "price": 10.50,
            "pages": 120,
            "rating": 7.5,
        },
    )

    assert response.status_code == 400
    body = response.get_json()
    assert "message" in body
    assert "link" in body["message"]


def test_get_book_contains_all_fields(client):
    create_response = client.post(
        "/books",
        json={
            "title": "Book title",
            "description": "desc",
            "link": "https://example.com/book",
            "author": "Author name",
            "price": 25.99,
            "pages": 321,
            "rating": 8.7,
        },
    )
    created_book = create_response.get_json()

    response = client.get(f"/books/{created_book['id']}")
    data = response.get_json()

    assert response.status_code == 200
    assert set(data.keys()) == {
        "id",
        "title",
        "description",
        "link",
        "author",
        "price",
        "pages",
        "rating",
        "created_at",
        "updated_at",
    }


def test_create_book_persists_record(client):
    payload = {
        "title": "Domain-driven design",
        "description": "Software design principles",
        "link": "https://example.com/ddd",
        "author": "Eric Evans",
        "price": 31.49,
        "pages": 560,
        "rating": 9.2,
    }
    create_response = client.post("/books", json=payload)
    created = create_response.get_json()

    get_response = client.get(f"/books/{created['id']}")
    fetched = get_response.get_json()

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert fetched["id"] == created["id"]
    assert fetched["title"] == payload["title"]
    assert fetched["description"] == payload["description"]
    assert fetched["link"] == payload["link"]
    assert fetched["author"] == payload["author"]
    assert fetched["price"] == payload["price"]
    assert fetched["pages"] == payload["pages"]
    assert fetched["rating"] == payload["rating"]


def test_update_book_updates_values(client):
    create_response = client.post(
        "/books",
        json={
            "title": "Old title",
            "description": "Old description",
            "link": "https://example.com/old",
            "author": "Old author",
            "price": 11.00,
            "pages": 200,
            "rating": 6.1,
        },
    )
    book_id = create_response.get_json()["id"]

    update_payload = {
        "title": "New title",
        "description": "New description",
        "link": "https://example.com/new",
        "author": "New author",
        "price": 15.75,
        "pages": 275,
        "rating": 8.3,
    }
    update_response = client.put(f"/books/{book_id}", json=update_payload)
    updated = update_response.get_json()
    get_response = client.get(f"/books/{book_id}")
    fetched = get_response.get_json()

    assert update_response.status_code == 200
    assert updated["title"] == update_payload["title"]
    assert updated["description"] == update_payload["description"]
    assert updated["link"] == update_payload["link"]
    assert updated["author"] == update_payload["author"]
    assert updated["price"] == update_payload["price"]
    assert updated["pages"] == update_payload["pages"]
    assert updated["rating"] == update_payload["rating"]
    assert get_response.status_code == 200
    assert fetched["title"] == update_payload["title"]
    assert fetched["description"] == update_payload["description"]
    assert fetched["link"] == update_payload["link"]
    assert fetched["author"] == update_payload["author"]
    assert fetched["price"] == update_payload["price"]
    assert fetched["pages"] == update_payload["pages"]
    assert fetched["rating"] == update_payload["rating"]
