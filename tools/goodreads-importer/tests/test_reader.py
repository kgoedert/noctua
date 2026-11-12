from pathlib import Path

import pytest
from goodreads_importer.reader import read_csv


def test_read_file_returns_two_records(tmp_path: Path):
    content_file = tmp_path / "goodreads_data.csv"

    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
22875447,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
'''

    content_file.write_text(contents, encoding="utf-8")

    books: list[dict[str, str]] = list(read_csv(content_file))

    assert len(books) == 2
    first_book = books[0]
    second_book = books[1]

    assert (
        first_book["Title"]
        == "Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead"
    )
    assert first_book["Author"] == "Laszlo Bock"
    assert first_book["Author l-f"] == "Bock, Laszlo"

    assert (second_book["Author"]) == "Nassim Nicholas Taleb"


def test_read_file_with_only_header(tmp_path: Path):
    content_file = tmp_path / "goodreads_only_header.csv"
    contents = "Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies"

    content_file.write_text(contents, encoding="utf-8")

    books: list[dict[str, str]] = list(read_csv(content_file))

    assert len(books) == 0


def test_read_empty_file(tmp_path: Path):
    content_file = tmp_path / "empty_file.csv"
    content_file.touch()

    books: list[dict[str, str]] = list(read_csv(content_file))

    assert len(books) == 0


def test_read_non_existing_file(tmp_path: Path):
    content_file = tmp_path / "non_existing_file.csv"

    with pytest.raises(FileNotFoundError):
        list(read_csv(content_file))


def test_read_special_characters(tmp_path: Path):
    content_file = tmp_path / "special_characters.csv"
    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
34862877,D. Leopoldina - A História não Contada: A Mulher que Arquitetou a Independência do Brasil,Paulo Rezzutti,"Rezzutti, Paulo",,"=""8544105106""","=""9788544105108""",4.0,LeYa,Paperback,464,2017,2017,2022/07/09,2022/06/29,,,read,,,,1,0
'''
    content_file.write_text(contents, encoding="utf-8")

    books: list[dict[str, str]] = list(read_csv(content_file))

    assert len(books) == 1

    assert (
        books[0]["Title"]
        == "D. Leopoldina - A História não Contada: A Mulher que Arquitetou a Independência do Brasil"
    )


def test_additional_authors_are_correctly_kept(tmp_path: Path):
    content_file = tmp_path / "additional_authors.csv"
    contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
7190,The Three Musketeers,Alexandre Dumas,"Dumas, Alexandre","Richard Pevear, Philip Bates, William Barrow, August Zoller, Marisa Zini, Moshe Ukkle, Pierre Toutain-Dorbec, John      Lee, Jacques Georges Clemenc Le Clercq, Natalie Montoto, S.M. Sheley, Daniel Rasmusson, Louis Jourdan, Walter Covell, Michael  Page, Michael Hugh Johnson, Sylvie Thorel-Cailleteau, Milo Winter, Bill Homewood, Arthur Paul John Charles James Gore Sudley, S.N. Rizvi, Giorgio Manganelli, William Robson, Isabel Ely Lord","=""""","=""""",0,Modern Library,Paperback,625,2001,1844,2025/10/25,2016/04/12,,,read,,,,1,0
'''
    content_file.write_text(contents, encoding="utf-8")

    books: list[dict[str, str]] = list(read_csv(content_file))

    assert len(books) == 1
    assert len(books[0]["Additional Authors"].split(sep=", ")) == 24
