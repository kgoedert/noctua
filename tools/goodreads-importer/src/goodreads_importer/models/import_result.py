from goodreads_importer.models.base_noctua_model import BaseNoctuaModel
from goodreads_importer.models.book import Book


class ImportRecordError(BaseNoctuaModel):
    record_number: int
    message: str


class GoodreadsImportResult(BaseNoctuaModel):
    books: list[Book]
    total_records: int
    imported_records: int
    rejected_records: int
    errors: list[ImportRecordError]
