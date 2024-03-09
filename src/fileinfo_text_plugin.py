# --- START fileinfo_text_plugin ---
"""Plugin for fileinfo for TXT files."""

from collections.abc import Iterable
from pathlib import Path

from fileinfo.plugins import file_type


@file_type(r"\.txt")
def process_txt(path: Path) -> Iterable[str]:
    """Process a TXT file.

    Args:
        path: Path of the file to check.

    Yields:
        Information on number of lines and number of words.
    """
    contents = path.read_text()
    yield f"Lines {len(contents.split('\n'))}"
    yield f"Words {len(contents.split())}"


# --- END fileinfo_text_plugin ---
