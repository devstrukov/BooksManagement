from datetime import datetime


class BookDTO:
    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        link: str,
        author: str,
        price: float,
        pages: int,
        rating: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._id = id
        self._title = title
        self._description = description
        self._link = link
        self._author = author
        self._price = price
        self._pages = pages
        self._rating = rating
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def link(self) -> str:
        return self._link

    @property
    def author(self) -> str:
        return self._author

    @property
    def price(self) -> float:
        return self._price

    @property
    def pages(self) -> int:
        return self._pages

    @property
    def rating(self) -> float:
        return self._rating

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at
