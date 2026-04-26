from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from domain.book_dto import BookDTO


class BookRepository(ABC):
    @abstractmethod
    def get_book_by_id(self, book_id: int) -> Optional[BookDTO]:
        """Returns a BookDTO by ID or None when not found."""

    @abstractmethod
    def list_books(self, sort_by: str, order: str) -> list[BookDTO]:
        """Returns all books sorted by provided field and order."""

    @abstractmethod
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
        """Creates a new book and returns it."""

    @abstractmethod
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
        """Updates existing book and returns it, or None if not found."""

    @abstractmethod
    def delete_book(self, book_id: int) -> bool:
        """Deletes book by ID and returns success flag."""

    @abstractmethod
    def get_id_stats(self) -> dict[str, float | int | None]:
        """Returns aggregate statistics for numeric book fields."""
