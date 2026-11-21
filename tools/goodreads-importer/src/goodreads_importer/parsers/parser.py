import csv
import logging
from collections.abc import Iterator
from datetime import date, datetime
from typing import TextIO

from goodreads_importer.exceptions import InvalidGoodreadsFileError
from goodreads_importer.models.book import Book
from goodreads_importer.models.import_result import (
    GoodreadsImportResult,
    ImportRecordError,
)
from goodreads_importer.parsers.reader import read_csv

logger = logging.getLogger(__name__)


def import_goodreads_file(goodreads_stream: TextIO) -> GoodreadsImportResult:
    result: GoodreadsImportResult = GoodreadsImportResult(
        books=[],
        total_records=0,
        imported_records=0,
        rejected_records=0,
        errors=[],
    )

    validate_file(goodreads_stream)

    for record in read_goodreads_books(goodreads_stream):
        if isinstance(record, Book):
            result.books.append(record)
            result.imported_records = result.imported_records + 1
        else:
            result.errors.append(record)
            result.rejected_records = result.rejected_records + 1
    result.total_records = result.imported_records + result.rejected_records

    return result


def read_goodreads_books(
    goodreads_stream: TextIO,
) -> Iterator[Book | ImportRecordError]:
    for record_number, record in enumerate(read_csv(goodreads_stream), start=1):
        try:
            book = parse_goodreads_book(record)
            yield book
        except ValueError as error:
            logger.warning(
                "Could not import Goodreads record %s: %s", record_number, error
            )
            yield ImportRecordError(message=str(error), record_number=record_number)


def parse_goodreads_book(book_record: dict[str, str]) -> Book:
    book_id: str | None = book_record.get("Book Id")
    book_title: str | None = book_record.get("Title")

    if book_id is None or not book_id.strip():
        raise ValueError("Book id missing. Record cannot be imported.")

    if book_title is None or not book_title.strip():
        raise ValueError(f"The book title is missing in book with book id = {book_id}")

    all_authors: list[str] = []
    author: str = book_record.get("Author")
    if author is not None:
        author = author.strip()
        if author != "":
            all_authors.append(author)

    if book_record.get("Additional Authors") is not None:
        for author in book_record.get("Additional Authors").split(", "):
            if author.strip():
                all_authors.append(author.strip())

    return Book(
        authors=all_authors,
        date_added=parse_date_field(book_record.get("Date Added")),
        date_read=parse_date_field(book_record.get("Date Read")),
        goodreads_id=book_id.strip(),
        isbn=parse_formula_field(book_record.get("ISBN")),
        isbn13=parse_formula_field(book_record.get("ISBN13")),
        rating=parse_float_field(book_record.get("My Rating")),
        read_count=parse_int_field(book_record.get("Read Count")),
        reading_status=(book_record.get("Exclusive Shelf") or "").strip(),
        title=book_title.strip(),
    )


def parse_date_field(date_field: str | None) -> date | None:
    if date_field is None:
        return None

    date_field = date_field.strip()

    if date_field == "":
        return None

    return datetime.strptime(date_field, "%Y/%m/%d").date()


def parse_float_field(float_field: str | None) -> float | None:
    if float_field:
        float_field = float_field.strip()

    if float_field is not None and float_field != "":
        ff: float = float(float_field)
        if ff != 0.0:
            return ff
    return None


def parse_formula_field(formula_field: str | None) -> str | None:
    if formula_field:
        formula_field = formula_field.strip()

    if formula_field is not None and formula_field != "":
        return formula_field.replace("=", "").replace('"', "")
    return None


def parse_int_field(int_field: str | None) -> int | None:
    if int_field:
        int_field = int_field.strip()

    if int_field is not None and int_field != "":
        return int(int_field)
    return None


def validate_file(goodreads_stream: TextIO):
    reader = csv.DictReader(goodreads_stream)

    headers = reader.fieldnames

    if not headers or not "Book Id" in headers or not "Title" in headers:
        raise InvalidGoodreadsFileError(
            "Missing one or more required headers. 'Book Id' and/or 'Title'"
        )
    goodreads_stream.seek(0)
