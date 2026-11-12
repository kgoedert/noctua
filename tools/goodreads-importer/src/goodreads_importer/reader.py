import csv
from collections.abc import Iterator
from pathlib import Path


def read_csv(file_path: Path) -> Iterator[dict[str, str]]:

    with file_path.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        yield from reader
