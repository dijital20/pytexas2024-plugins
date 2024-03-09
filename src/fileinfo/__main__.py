"""Command line interface."""

# --- START imports and globals ---
import argparse
import logging
import re
from pathlib import Path

from .plugins import FileInfoHandlerFunction, find_all_functions

LOG = logging.getLogger(__name__)
# --- END imports and globals ---


# --- START CLI ---
def _get_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get information on files.")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    parser.add_argument("path", nargs="+", type=Path, help="Paths to search.")

    return parser.parse_args()


# --- END CLI ---


# --- START Iterate paths ---
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
                if child.is_file():
                    file_paths.add(child)
    return sorted(file_paths)


# --- END Iterate paths ---


# --- START File processor ---
def process_file(
    path: Path,
    processor_functions: list[tuple[str, FileInfoHandlerFunction]],
):
    """Process a single file path.

    Args:
        path: Path of the file.
        processor_functions: List of 2-element tuples, containing a file
            extension regular expression, and a corresponding function.
    """
    LOG.debug("--> Processing file %s (%r)", path, path.suffix)
    for pattern, processor in processor_functions:
        if not re.match(pattern, path.suffix):
            continue

        LOG.debug("==> Calling %s", processor)
        try:
            LOG.info("\n".join(map(str, processor(path))))
        except Exception:
            LOG.debug(
                "ERROR running %s on %s",
                processor,
                path,
                exc_info=True,
            )

    LOG.debug("<-- Finished %s", path)
    LOG.info("")


# --- END File processor ---

# --- START main ---
if __name__ == "__main__":
    args = _get_command_line()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    processors = find_all_functions()

    for path in find_all_files(args.path):
        process_file(path, processors)
# --- END main ---
