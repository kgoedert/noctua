import logging
from datetime import datetime
from io import StringIO
from pathlib import Path

import pytest
from goodreads_importer.exceptions import InvalidGoodreadsFileError
from goodreads_importer.models.book import Book
from goodreads_importer.models.import_result import (
    GoodreadsImportResult,
    ImportRecordError,
)
from goodreads_importer.parsers.parser import (
    import_goodreads_file,
    parse_date_field,
    parse_float_field,
    parse_formula_field,
    parse_goodreads_book,
    parse_int_field,
    read_goodreads_books,
    validate_file,
)


def test_float_parser():
    assert parse_float_field("5.0") == 5.0
    assert parse_float_field("1.0") == 1.0
    assert parse_float_field("0") is None
    assert parse_float_field("0.0") is None
    assert parse_float_field("") is None
    assert parse_float_field("      ") is None
    assert parse_float_field(None) is None


def test_int_parser():
    assert parse_int_field("1") == 1
    assert parse_int_field("0") == 0
    assert parse_int_field("") is None
    assert parse_int_field("    ") is None
    assert parse_int_field(None) is None


def test_parse_formula_field():
    assert parse_formula_field("=1455554790") == "1455554790"
    assert parse_formula_field('="1455554790"') == "1455554790"
    assert parse_formula_field("") is None
    assert parse_formula_field("     ") is None
    assert parse_formula_field(None) is None


def test_parse_date_field():
    assert (
        parse_date_field("2026/11/07")
        == datetime.strptime("2026/11/07", "%Y/%m/%d").date()
    )
    assert (
        parse_date_field(" 2026/11/07 ")
        == datetime.strptime("2026/11/07", "%Y/%m/%d").date()
    )
    assert parse_date_field("") is None
    assert parse_date_field("       ") is None
    assert parse_date_field(None) is None


def test_record_without_id_raises_error():
    book: dict[str, str] = {
        "Author": "Leo Tolstoy",
        "Title": "Leo Tolstoy",
        "Additional Authors": "Aylmer Maude, Louise Maude",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    with pytest.raises(ValueError) as exception:
        parse_goodreads_book(book)

    assert str(exception.value) == "Book id missing. Record cannot be imported."


def test_record_without_title_raises_error():
    book: dict[str, str] = {
        "Author": "Leo Tolstoy",
        "Book Id": "656",
        "Additional Authors": "Aylmer Maude, Louise Maude",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    with pytest.raises(ValueError) as exception:
        parse_goodreads_book(book)

    assert (
        str(exception.value) == "The book title is missing in book with book id = 656"
    )


def test_record_author_parsed_correctly():
    book: dict[str, str] = {
        "Author": "    Leo Tolstoy   ",
        "Book Id": "656",
        "Title": "War and Peace",
        "Additional Authors": "Aylmer Maude, Louise Maude",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    parsed_book = parse_goodreads_book(book)

    assert "Leo Tolstoy" in parsed_book.authors


def test_record_additional_authors_parsed_correctly():
    book: dict[str, str] = {
        "Author": "    Leo Tolstoy   ",
        "Book Id": "656",
        "Title": "War and Peace",
        "Additional Authors": "  Aylmer Maude, Louise Maude ",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    parsed_book = parse_goodreads_book(book)

    assert "Leo Tolstoy" in parsed_book.authors
    assert "Aylmer Maude" in parsed_book.authors
    assert "Louise Maude" in parsed_book.authors
    assert parsed_book.authors[0] == "Leo Tolstoy"
    assert len(parsed_book.authors) == 3


def test_author_has_only_whitespaces():
    book: dict[str, str] = {
        "Author": "       ",
        "Book Id": "656",
        "Title": "War and Peace",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    parsed_book = parse_goodreads_book(book)

    assert len(parsed_book.authors) == 0


def test_no_authors():
    book: dict[str, str] = {
        "Book Id": "656",
        "Title": "War and Peace",
        "ISBN": '"0192833987""',
        "ISBN13": '=""9780192833983""',
    }

    parsed_book = parse_goodreads_book(book)

    assert len(parsed_book.authors) == 0


def test_read_multiple_records(tmp_path: Path):
    content_file = tmp_path / "goodreads_data.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
22875447,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with open(content_file) as f:
        books: list[Book] = list(read_goodreads_books(f))

    assert len(books) == 2
    assert "Laszlo Bock" in books[0].authors
    assert books[1].title == "Skin in the Game: The Hidden Asymmetries in Daily Life"


def test_read_empty_file(tmp_path: Path):
    content_file = tmp_path / "goodreads_data.csv"

    content_file.touch()

    with open(content_file) as f:
        books: list[Book] = list(read_goodreads_books(f))

    assert len(books) == 0


def test_read_inconsistent_record(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    content_file = tmp_path / "goodreads_data.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with caplog.at_level(logging.WARNING), open(content_file) as f:
        books: list[Book | ImportRecordError] = list(read_goodreads_books(f))

    assert len(books) == 2
    assert books[1].title == "Skin in the Game: The Hidden Asymmetries in Daily Life"
    assert (
        "Could not import Goodreads record 1: Book id missing. Record cannot be imported."
        in caplog.text
    )


def test_import_fully_consistent_file(tmp_path: Path):
    content_file = tmp_path / "fully_consistent.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
22875447,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
31866,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with open(content_file) as f:
        result: GoodreadsImportResult = import_goodreads_file(f)

    assert result.total_records == 3
    assert result.rejected_records == 0
    assert result.imported_records == 3
    assert len(result.books) == 3
    assert len(result.errors) == 0
    assert result.books[2].goodreads_id == "31866"
    assert "Laszlo Bock" in result.books[0].authors
    assert (
        result.books[1].title
        == "Skin in the Game: The Hidden Asymmetries in Daily Life"
    )


def test_import_fully_inconsistent_file(tmp_path: Path):
    content_file = tmp_path / "fully_inconsistent.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with open(content_file) as f:
        result: GoodreadsImportResult = import_goodreads_file(f)

    assert result.total_records == 3
    assert result.rejected_records == 3
    assert result.imported_records == 0
    assert len(result.books) == 0
    assert len(result.errors) == 3
    assert result.errors[0].message == "Book id missing. Record cannot be imported."
    assert result.errors[0].record_number == 1
    assert (
        result.errors[1].message
        == "The book title is missing in book with book id = 36064445"
    )
    assert result.errors[1].record_number == 2
    assert result.errors[2].message == "Book id missing. Record cannot be imported."
    assert result.errors[2].record_number == 3


def test_import_mixed_consistent_inconsistent_file(tmp_path: Path):
    content_file = tmp_path / "mixed.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with open(content_file) as f:
        result: GoodreadsImportResult = import_goodreads_file(f)

    assert result.total_records == 3
    assert result.rejected_records == 2
    assert result.imported_records == 1
    assert len(result.books) == 1
    assert len(result.errors) == 2
    assert result.errors[0].message == "Book id missing. Record cannot be imported."
    assert result.errors[0].record_number == 1
    assert (
        result.books[0].title
        == "Skin in the Game: The Hidden Asymmetries in Daily Life"
    )
    assert result.errors[1].message == "Book id missing. Record cannot be imported."
    assert result.errors[1].record_number == 3


def test_import_empty_file(tmp_path: Path):
    content_file = tmp_path / "empty.csv"

    content_file.touch()

    with (
        open(content_file) as f,
        pytest.raises(
            InvalidGoodreadsFileError,
            match="Missing one or more required headers. 'Book Id' and/or 'Title'",
        ),
    ):
        import_goodreads_file(f)


def test_import_header_only_file(tmp_path: Path):
    content_file = tmp_path / "header_only.csv"

    contents = """Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies"""

    content_file.write_text(contents, encoding="utf-8")

    with open(content_file) as f:
        result: GoodreadsImportResult = import_goodreads_file(f)

    assert result.books == []
    assert result.errors == []
    assert result.rejected_records == 0
    assert result.imported_records == 0
    assert result.total_records == 0


def test_import_book_id_header_missing(tmp_path: Path):
    content_file = tmp_path / "missing_book_id.csv"

    contents = '''Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
    ,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
    36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
    ,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
    '''

    content_file.write_text(contents, encoding="utf-8")

    with (
        open(content_file) as f,
        pytest.raises(
            InvalidGoodreadsFileError,
            match="Missing one or more required headers. 'Book Id' and/or 'Title'",
        ),
    ):
        import_goodreads_file(f)


def test_import_title_header_missing(tmp_path: Path):
    content_file = tmp_path / "missing_book_title.csv"

    contents = '''Book Id,,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
    ,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
    36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
    ,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
    '''

    content_file.write_text(contents, encoding="utf-8")

    with (
        open(content_file) as f,
        pytest.raises(
            InvalidGoodreadsFileError,
            match="Missing one or more required headers. 'Book Id' and/or 'Title'",
        ),
    ):
        import_goodreads_file(f)


def test_import_title_book_id_header_missing(tmp_path: Path):
    content_file = tmp_path / "missing_book_id_title.csv"

    contents = '''Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
    ,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
    36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
    ,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
    '''

    content_file.write_text(contents, encoding="utf-8")

    with (
        open(content_file) as f,
        pytest.raises(
            InvalidGoodreadsFileError,
            match="Missing one or more required headers. 'Book Id' and/or 'Title'",
        ),
    ):
        import_goodreads_file(f)


def test_import_header_whitespace(tmp_path: Path):
    content_file = tmp_path / "missing_book_id_title.csv"

    contents = '''   Book Id,   Title   ,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
    ,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
    36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
    ,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
    '''

    content_file.write_text(contents, encoding="utf-8")

    with (
        open(content_file) as f,
        pytest.raises(
            InvalidGoodreadsFileError,
            match="Missing one or more required headers. 'Book Id' and/or 'Title'",
        ),
    ):
        import_goodreads_file(f)


def test_validate_file_stream_at_start():
    stream = StringIO(
        "Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies"
    )

    validate_file(stream)

    assert stream.tell() == 0
