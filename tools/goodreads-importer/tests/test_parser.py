import logging
from datetime import datetime
from pathlib import Path

import pytest
from goodreads_importer.models.book import Book
from goodreads_importer.parser import (
    parse_date_field,
    parse_float_field,
    parse_formula_field,
    parse_goodreads_book,
    parse_int_field,
    read_goodreads_books,
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

    books: list[Book] = list(read_goodreads_books(content_file))

    assert len(books) == 2
    assert "Laszlo Bock" in books[0].authors
    assert books[1].title == "Skin in the Game: The Hidden Asymmetries in Daily Life"


def test_read_empty_file(tmp_path: Path):
    content_file = tmp_path / "goodreads_data.csv"

    content_file.touch()

    books: list[Book] = list(read_goodreads_books(content_file))

    assert len(books) == 0


def test_read_inconsistent_record(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    content_file = tmp_path / "goodreads_data.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        books: list[Book] = list(read_goodreads_books(content_file))

    assert len(books) == 1
    assert books[0].title == "Skin in the Game: The Hidden Asymmetries in Daily Life"
    assert (
        "Could not import Goodreads record 1: Book id missing. Record cannot be imported."
        in caplog.text
    )
