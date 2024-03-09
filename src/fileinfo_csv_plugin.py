# --- START fileinfo_csv_plugin ---
"""Plugin for fileinfo for CSV files."""

from collections.abc import Iterable
from csv import reader
from pathlib import Path

from fileinfo.plugins import file_type


@file_type(r"\.csv")
def process_csv(path: Path) -> Iterable[str]:
    """Process a CSV file.

    Args:
        path: Path of the file to check.

    Yields:
        Information on columns and rows.
    """
    with path.open(mode="r") as f:
        contents = list(reader(f))

    yield f"Rows {len(contents)}"
    yield f"Columns {max(len(r) for r in contents)}"


# --- END fileinfo_csv_plugin ---
