import importlib
import inspect
import logging
import pkgutil
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

# This is the signature of a function that could be decorated.
FileInfoHandlerFunction = Callable[[Path], Iterable[str]]
# This is a TypeVar to indicate that we get out what we put in.
F = TypeVar("F", bound=FileInfoHandlerFunction)


# --- START Decorator ---
LOG = logging.getLogger(__name__)
ATTR_NAME = "_fileinfo_registered_type"


def file_type(*patterns: str) -> Callable[[F], F]:
    """Decorates a callable to indicate that it handles a certain type.

    Args:
        pattern: Regex patterns of the file extension to match.

    Returns:
        A decorator function that returns the original function, but with
        additional attributes to mark the function.
    """

    def wrapper(func: F) -> F:
        """Wraps a callable to mark it for a given type."""
        LOG.debug("Registering %s to %s", func, patterns)
        if isinstance(
            (registered_types := getattr(func, ATTR_NAME, None)),
            set,
        ):
            LOG.debug("Adding to existing set")
            registered_types.update(patterns)
        else:
            LOG.debug("Creating new set")
            setattr(func, ATTR_NAME, {*patterns})

        return func

    return wrapper


# --- END Decorator ---


# --- START Predicate ---
# ATTR_NAME defined in previous example...
def _is_plugin_func(obj: Any) -> bool:
    """Predicate function for finding a plugin registered function.

    Args:
        obj: Object to test.

    Returns:
        True if this is a function with the _fileinfo_registered_types
        attribute, and False otherwise.
    """
    return inspect.isfunction(obj) and hasattr(obj, ATTR_NAME)


# --- END Predicate ---


# --- START Function Finder ---
def _find_functions_in_module(
    module_name: str,
) -> list[tuple[str, FileInfoHandlerFunction]]:
    """Find all of the functions within a given module by name.

    Args:
        module_name: Name of the module to import.

    Returns:
        List of matching functions.
    """
    found_handlers = []
    LOG.debug("Importing %s", module_name)
    try:
        module = importlib.import_module(module_name)
    except Exception:
        LOG.debug("Skipping %s due to import error", module_name)
    else:
        for _, func in inspect.getmembers(module, _is_plugin_func):
            for type_pattern in getattr(func, ATTR_NAME):
                LOG.debug("Adding %r for %s", type_pattern, func)
                found_handlers.append((type_pattern, func))

    return found_handlers


# --- END Function Finder ---


# --- START Plugin Finder ---
def find_all_functions() -> list[tuple[str, FileInfoHandlerFunction]]:
    """Find all functions that can be registered to a type.

    Returns:
        List of tuples, containing the type patterns and their associated
        functions.
    """
    found_handlers = []
    LOG.debug("--> Finding handler plugins")

    # Add the default behavior
    found_handlers += _find_functions_in_module(__name__)

    # Search all top-level packages/modules
    for _, module_name, is_pkg in pkgutil.iter_modules():
        # If it doesn't start with fileinfo and end with plugin, skip it!
        if not all(
            (
                module_name.startswith("fileinfo"),
                module_name.endswith("plugin"),
            )
        ):
            LOG.debug("Skipping %s", module_name)
            continue

        if is_pkg:
            # If this is a package, walk it, so we can search each submodule
            LOG.debug("Importing %s for submodules", module_name)
            try:
                module = importlib.import_module(module_name)
            except Exception:
                LOG.debug(
                    "Skipping %s due to error", module_name, exc_info=True
                )
            else:
                for _, module_name, _ in pkgutil.walk_packages(module.__path__):
                    found_handlers += _find_functions_in_module(module_name)

        else:
            found_handlers += _find_functions_in_module(module_name)

    LOG.debug("<-- Found %d handler functions", len(found_handlers))
    return found_handlers


# --- END Plugin Finder ---


# --- START Default handler ---
@file_type(".*")
def default(path: Path) -> Iterable[str]:
    """Default handler for any file type.

    Args:
        path: Path to examine.

    Returns:
        Information on the file as lines of text.
    """
    yield f"{path.resolve()}"
    yield f"{path.suffix.upper()} file" if path.suffix else "File"
    yield f"{path.stat().st_size} bytes"


# --- END Default handler ---
