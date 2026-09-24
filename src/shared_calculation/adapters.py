"""Optional source-format adapters."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, TextIO, Union

CsvSource = Union[str, Path, TextIO]


def read_csv_records(source: CsvSource, *, encoding: str = "utf-8", delimiter: str = ",") -> Iterable[Mapping[str, str]]:
    """Read CSV rows as mappings without coupling the calculation core to CSV."""
    if hasattr(source, "read"):
        return list(csv.DictReader(source, delimiter=delimiter))
    with Path(source).open("r", encoding=encoding, newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))
