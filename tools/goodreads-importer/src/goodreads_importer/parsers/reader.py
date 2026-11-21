import csv
from collections.abc import Iterator
from typing import TextIO


def read_csv(goodreads_stream: TextIO) -> Iterator[dict[str, str]]:
    """Expects the sream to be positioned at the beginning"""
    reader = csv.DictReader(goodreads_stream)

    yield from reader
