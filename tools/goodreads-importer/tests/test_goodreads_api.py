from pathlib import Path

from fastapi.testclient import TestClient
from goodreads_importer.api import main


def test_import_valid_file(tmp_path: Path):
    file = tmp_path / "valid_file.csv"

    file_contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
22875447,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
31866,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
656,War and Peace,Leo Tolstoy,"Tolstoy, Leo","Aylmer Maude, Louise Maude","=""0192833987""","=""9780192833983""",0,Oxford University Press,Paperback,1392,1998,1868,,2012/08/13,currently-reading,currently-reading (#1),currently-reading,,,,1,0'''

    file.write_text(file_contents, encoding="utf-8")

    client = TestClient(main.app)

    with open(file, "rb") as upload:
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data["books"]) == 4
        assert response_data["totalRecords"] == 4
        assert response_data["importedRecords"] == 4
        assert response_data["rejectedRecords"] == 0
        assert response_data["errors"] == []
        assert response_data["books"][3]["title"] == "War and Peace"
        assert "Frederick Charles Copleston" in response_data["books"][2]["authors"]
        assert response_data["books"][1]["dateRead"] == "2026-11-07"


def test_import_valid_invalid_records_file(tmp_path: Path):
    file = tmp_path / "valid_invalid_file.csv"

    file_contents = '''Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
31866,,Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
656,War and Peace,Leo Tolstoy,"Tolstoy, Leo","Aylmer Maude, Louise Maude","=""0192833987""","=""9780192833983""",0,Oxford University Press,Paperback,1392,1998,1868,,2012/08/13,currently-reading,currently-reading (#1),currently-reading,,,,1,0'''

    file.write_text(file_contents, encoding="utf-8")

    client = TestClient(main.app)

    with open(file, "rb") as upload:
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data["books"]) == 2
        assert response_data["totalRecords"] == 4
        assert response_data["importedRecords"] == 2
        assert response_data["rejectedRecords"] == 2
        assert len(response_data["errors"]) == 2
        assert response_data["books"][1]["title"] == "War and Peace"
        assert "Nassim Nicholas Taleb" in response_data["books"][0]["authors"]
        assert response_data["errors"][0]["recordNumber"] == 1
        assert (
            response_data["errors"][0]["message"]
            == "Book id missing. Record cannot be imported."
        )
        assert response_data["errors"][1]["recordNumber"] == 3
        assert (
            response_data["errors"][1]["message"]
            == "The book title is missing in book with book id = 31866"
        )


def test_import_empty_file(tmp_path: Path):
    file = tmp_path / "empty_file.csv"

    file.touch()

    client = TestClient(main.app)

    with (
        open(file, "rb") as upload,
    ):
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "The uploaded file is not a valid Goodreads CSV export. Required headers: 'Book Id' and 'Title'."
        )


def test_import_only_header_file(tmp_path: Path):
    file = tmp_path / "only_header_file.csv"

    file_contents = """Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies"""

    file.write_text(file_contents, encoding="utf-8")

    client = TestClient(main.app)

    with open(file, "rb") as upload:
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data["books"]) == 0
        assert response_data["totalRecords"] == 0
        assert response_data["importedRecords"] == 0
        assert response_data["rejectedRecords"] == 0
        assert len(response_data["errors"]) == 0


def test_missing_file():
    client = TestClient(main.app)

    response = client.post("/import-goodreads-data")

    assert response.status_code == 422


def test_import_invalid_characters_file(tmp_path: Path):
    file = tmp_path / "invalid_characters_file.csv"

    file.write_bytes(b"Book Id,Title\n123,War and Peace\xff\n")

    client = TestClient(main.app)

    with open(file, "rb") as upload:
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"] == "The uploaded file must be encoded in UTF-8."
        )


def test_import_missing_required_headers_file(tmp_path: Path):
    file = tmp_path / "missing_required_headers_file.csv"

    file_contents = '''Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Publisher,Binding,Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Owned Copies
22875447,Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead,Laszlo Bock,"Bock, Laszlo",,"=""1455554790""","=""9781455554799""",0,Twelve,Hardcover,406,2015,2015,,2026/11/07,currently-reading,currently-reading (#3),currently-reading,,,,1,0
36064445,Skin in the Game: The Hidden Asymmetries in Daily Life,Nassim Nicholas Taleb,"Taleb, Nassim Nicholas",,"=""0241300657""","=""9780241300657""",5.0,Allen Lane,Paperback,272,2018,2018,2026/11/07,2026/10/17,,,read,,,,1,0
31866,"A History of Philosophy, Vol. 1: Greece and Rome, From the Pre-Socratics to Plotinus",Frederick Charles Copleston,"Copleston, Frederick Charles",,"=""0385468431""","=""9780385468435""",0,Image,Paperback,521,1993,1946,,2026/10/17,currently-reading,currently-reading (#2),currently-reading,,,,1,0
656,War and Peace,Leo Tolstoy,"Tolstoy, Leo","Aylmer Maude, Louise Maude","=""0192833987""","=""9780192833983""",0,Oxford University Press,Paperback,1392,1998,1868,,2012/08/13,currently-reading,currently-reading (#1),currently-reading,,,,1,0'''

    file.write_text(file_contents, encoding="utf-8")

    client = TestClient(main.app)

    with open(file, "rb") as upload:
        response = client.post(
            "/import-goodreads-data",
            files={"goodreads_file": ("goodreads_file.csv", upload, "text/csv")},
        )

        assert response.status_code == 400

        assert (
            response.json()["detail"]
            == "The uploaded file is not a valid Goodreads CSV export. Required headers: 'Book Id' and 'Title'."
        )
