import io
from typing import TextIO

from fastapi import FastAPI, HTTPException, UploadFile

from goodreads_importer.exceptions import InvalidGoodreadsFileError
from goodreads_importer.models.import_result import GoodreadsImportResult
from goodreads_importer.parsers.parser import import_goodreads_file

app = FastAPI()


@app.post("/import-goodreads-data", response_model=GoodreadsImportResult)
def import_goodreads_data(goodreads_file: UploadFile) -> GoodreadsImportResult:

    text: TextIO = io.TextIOWrapper(goodreads_file.file, encoding="utf-8", newline="")
    try:
        result: GoodreadsImportResult = import_goodreads_file(text)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="The uploaded file must be encoded in UTF-8."
        )
    except InvalidGoodreadsFileError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid Goodreads CSV export. Required headers: 'Book Id' and 'Title'.",
        )
    finally:
        text.detach()

    return result
