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


if __name__ == "__main__":
    args = _get_command_line()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    processors = find_all_functions()

    LOG.debug("Processing %d paths", len(args.path))
    for path in args.path:
        for child in path.rglob("*"):
            if not child.is_file():
                continue

            for pattern, processor in processors:
                if not re.match(pattern, child.suffix):
                    continue

                for line in processor(child):
                    LOG.info(line)

            LOG.info("")
