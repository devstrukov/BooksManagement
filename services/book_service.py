from __future__ import annotations

from typing import Any

from domain.book_dto import BookDTO
from repositories.book_repository import BookRepository


class BookService:
    _UPDATABLE_FIELDS = frozenset(
        {"title", "description", "link", "author", "price", "pages", "rating"}
    )
    _ALLOWED_SORT_FIELDS = {
        "id",
        "title",
        "link",
        "author",
        "description",
        "price",
        "pages",
        "rating",
        "created_at",
        "updated_at",
    }
    _ALLOWED_ORDER = {"asc", "desc"}

    def __init__(self, book_repository: BookRepository) -> None:
        self._book_repository = book_repository

    def get_book_by_id(self, book_id: int) -> dict[str, Any] | None:
        book = self._book_repository.get_book_by_id(book_id)
        if book is None:
            return None
        return self._serialize_book(book)

    def list_books(self, sort_by: str | None, order: str | None) -> list[dict[str, Any]]:
        normalized_sort = self._normalize_sort_field(sort_by)
        normalized_order = self._normalize_order(order)
        books = self._book_repository.list_books(sort_by=normalized_sort, order=normalized_order)
        return [self._serialize_book(book) for book in books]

    def create_book(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = self._extract_non_empty_string(payload, "title")
        description = self._extract_non_empty_string(payload, "description")
        link = self._extract_non_empty_string(payload, "link")
        author = self._extract_non_empty_string(payload, "author")
        price = self._extract_positive_float(payload, "price")
        pages = self._extract_positive_int(payload, "pages")
        rating = self._extract_float_in_range(payload, "rating", min_value=0.0, max_value=10.0)

        book = self._book_repository.create_book(
            title=title,
            description=description,
            link=link,
            author=author,
            price=price,
            pages=pages,
            rating=rating,
        )
        return self._serialize_book(book)

    def update_book(self, book_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        current = self._book_repository.get_book_by_id(book_id)
        if current is None:
            return None

        fields_to_update = set(payload.keys()) & self._UPDATABLE_FIELDS
        unknown_fields = set(payload.keys()) - self._UPDATABLE_FIELDS
        if unknown_fields:
            unknown = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Unknown field(s): {unknown}")
        if not fields_to_update:
            raise ValueError("At least one updatable field must be provided")

        title = current.title
        description = current.description
        link = current.link
        author = current.author
        price = current.price
        pages = current.pages
        rating = current.rating

        if "title" in payload:
            title = self._extract_non_empty_string(payload, "title")
        if "description" in payload:
            description = self._extract_non_empty_string(payload, "description")
        if "link" in payload:
            link = self._extract_non_empty_string(payload, "link")
        if "author" in payload:
            author = self._extract_non_empty_string(payload, "author")
        if "price" in payload:
            price = self._extract_positive_float(payload, "price")
        if "pages" in payload:
            pages = self._extract_positive_int(payload, "pages")
        if "rating" in payload:
            rating = self._extract_float_in_range(payload, "rating", min_value=0.0, max_value=10.0)

        book = self._book_repository.update_book(
            book_id=book_id,
            title=title,
            description=description,
            link=link,
            author=author,
            price=price,
            pages=pages,
            rating=rating,
        )
        if book is None:
            return None
        return self._serialize_book(book)

    def delete_book(self, book_id: int) -> bool:
        return self._book_repository.delete_book(book_id=book_id)

    def get_book_stats(self) -> dict[str, float | int | None]:
        return self._book_repository.get_id_stats()

    def _normalize_sort_field(self, sort_by: str | None) -> str:
        if sort_by is None:
            return "id"
        normalized = sort_by.strip().lower()
        if normalized not in self._ALLOWED_SORT_FIELDS:
            raise ValueError(f"Unsupported sort_by value: {sort_by}")
        return normalized

    def _normalize_order(self, order: str | None) -> str:
        if order is None:
            return "ASC"
        normalized = order.strip().lower()
        if normalized not in self._ALLOWED_ORDER:
            raise ValueError(f"Unsupported order value: {order}")
        return normalized.upper()

    @staticmethod
    def _extract_non_empty_string(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{key}' is required and must be a non-empty string")
        return value.strip()

    @staticmethod
    def _extract_positive_float(payload: dict[str, Any], key: str) -> float:
        value = payload.get(key)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field '{key}' is required and must be a number")
        if parsed <= 0:
            raise ValueError(f"Field '{key}' must be greater than zero")
        return round(parsed, 2)

    @staticmethod
    def _extract_positive_int(payload: dict[str, Any], key: str) -> int:
        value = payload.get(key)
        if isinstance(value, bool):
            raise ValueError(f"Field '{key}' is required and must be an integer")
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field '{key}' is required and must be an integer")
        if parsed <= 0:
            raise ValueError(f"Field '{key}' must be greater than zero")
        return parsed

    @staticmethod
    def _extract_float_in_range(payload: dict[str, Any], key: str, min_value: float, max_value: float) -> float:
        value = payload.get(key)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field '{key}' is required and must be a number")
        if parsed < min_value or parsed > max_value:
            raise ValueError(f"Field '{key}' must be between {min_value} and {max_value}")
        return round(parsed, 1)

    @staticmethod
    def _serialize_book(book: BookDTO) -> dict[str, Any]:
        return {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "link": book.link,
            "author": book.author,
            "price": book.price,
            "pages": book.pages,
            "rating": book.rating,
            "created_at": book.created_at.isoformat(),
            "updated_at": book.updated_at.isoformat(),
        }
