"""Command line interface."""

import argparse
import logging
import re
from pathlib import Path

from .plugins import find_all_functions

LOG = logging.getLogger(__name__)


def _get_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get information on files.")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    parser.add_argument("path", nargs="+", type=Path, help="Paths to search.")

    return parser.parse_args()


def find_all_files(paths: list[Path]) -> list[Path]:
    """Find all of the file paths in a set of paths.

    Args:
        paths: List of paths to include.

    Returns:
        Sorted list of paths.
    """
    file_paths = set()
    for path in paths:
        if path.is_file():
            file_paths.add(path)
        else:
            for child in path.rglob("*"):
                file_paths.add(child)
    return sorted(file_paths)


def process_file(path: Path):
    """Process a single file path.

    Args:
        path: Path of the file.
    """
    LOG.debug("--> Processing file %s (%r)", path, path.suffix)
    for pattern, processor in processors:
        if not re.match(pattern, path.suffix):
            continue

        LOG.debug("==> Calling %s", processor)
        try:
            LOG.info("\n".join(processor(path)))
        except Exception:
            LOG.debug(
                "ERROR running %s on %s",
                processor,
                path,
                exc_info=True,
            )

    LOG.debug("<-- Finished %s", path)
    LOG.info("")


if __name__ == "__main__":
    args = _get_command_line()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    processors = find_all_functions()

    for path in find_all_files(args.path):
        process_file(path)
