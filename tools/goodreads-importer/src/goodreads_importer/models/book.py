from dataclasses import dataclass
from datetime import date


@dataclass
class Book:
    goodreads_id: str
    title: str
    authors: list[str]
    isbn: str | None
    isbn13: str | None
    reading_status: str | None
    rating: float | None
    date_added: date
    date_read: date | None
    read_count: int | None
