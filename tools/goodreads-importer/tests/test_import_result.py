from datetime import date

from goodreads_importer.models.book import Book
from goodreads_importer.models.import_result import (
    GoodreadsImportResult,
    ImportRecordError,
)


def test_import_multiple_books():
    book1: Book = Book(
        goodreads_id="1",
        title="War and Peace",
        authors=["Tolstoi"],
        isbn=None,
        isbn13=None,
        reading_status="currently-reading",
        rating=None,
        date_added=None,
        date_read=None,
        read_count=0,
    )
    book2: Book = Book(
        goodreads_id="2",
        title="Work Rules!",
        authors=["Lazlo"],
        isbn=None,
        isbn13=None,
        reading_status="currently-reading",
        rating=None,
        date_added=None,
        date_read=None,
        read_count=0,
    )

    books: list[Book] = [book1, book2]

    result: GoodreadsImportResult = GoodreadsImportResult(
        books=books, total_records=2, imported_records=2, rejected_records=0, errors=[]
    )

    assert result.books == books
    assert result.total_records == 2
    assert result.imported_records == 2
    assert result.rejected_records == 0
    assert result.errors == []


def test_import_with_rejected_records():
    book: Book = Book(
        goodreads_id="1",
        title="War and Peace",
        authors=["Tolstoi"],
        isbn=None,
        isbn13=None,
        reading_status="currently-reading",
        rating=None,
        date_added=None,
        date_read=None,
        read_count=0,
    )

    import_error: ImportRecordError = ImportRecordError(
        message="Error during import", record_number=1
    )

    books: list[Book] = [book]

    result: GoodreadsImportResult = GoodreadsImportResult(
        books=books,
        total_records=2,
        imported_records=1,
        rejected_records=1,
        errors=[import_error],
    )

    assert result.books == books
    assert result.total_records == 2
    assert result.imported_records == 1
    assert result.rejected_records == 1
    assert result.errors == [import_error]


def test_object_serialization():
    book: Book = Book(
        goodreads_id="1",
        title="War and Peace",
        authors=["Tolstoi"],
        isbn=None,
        isbn13=None,
        reading_status="currently-reading",
        rating=None,
        date_added=date(day=15, month=2, year=1980),
        date_read=None,
        read_count=0,
    )

    import_error: ImportRecordError = ImportRecordError(
        message="Error during import", record_number=1
    )

    result: GoodreadsImportResult = GoodreadsImportResult(
        books=[book],
        total_records=2,
        imported_records=1,
        rejected_records=1,
        errors=[import_error],
    )

    data = result.model_dump(by_alias=True)
    books: list[dict] = data["books"]
    errors: list[dict] = data["errors"]

    assert len(books) == 1
    assert len(errors) == 1
    assert books[0]["title"] == "War and Peace"
    assert errors[0]["message"] == "Error during import"
    assert books[0]["dateAdded"] == date(1980, 2, 15)
    assert books[0]["goodreadsId"] == "1"
    assert result.total_records == 2
    assert result.imported_records == 1
    assert result.rejected_records == 1


def test_object_deserialization():
    book: Book = Book(
        goodreads_id="1",
        title="War and Peace",
        authors=["Tolstoi"],
        isbn=None,
        isbn13=None,
        reading_status="currently-reading",
        rating=None,
        date_added=date(day=15, month=2, year=1980),
        date_read=None,
        read_count=0,
    )

    import_error: ImportRecordError = ImportRecordError(
        message="Error during import", record_number=1
    )

    result: GoodreadsImportResult = GoodreadsImportResult(
        books=[book],
        total_records=2,
        imported_records=1,
        rejected_records=1,
        errors=[import_error],
    )

    data_json = result.model_dump_json(by_alias=True)

    data: GoodreadsImportResult = result.model_validate_json(data_json)

    assert len(data.books) == 1
    assert data.books[0] == book
    assert len(data.errors) == 1
    assert data.errors[0] == import_error
    assert data.books[0].date_added == date(1980, 2, 15)
    assert result.total_records == 2
    assert result.imported_records == 1
    assert result.rejected_records == 1
