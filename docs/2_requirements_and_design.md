# Requirements and Design

## Base Application

We're going to make an application to print information about files, called `fileinfo`, given a directory. The base 
application will just print information common to any file type... the name, location, full path, and size.

### Event

Our `fileinfo` will **expose event, `found_type`, for each file extension that it encounters, which plugins should 
respond to in order to provide additional information**.

### Plugin Discovery

Our `fileinfo` will **discover plugins on its own by checking for top-level modules that begin with `fileinfo` and 
end with `plugin`**. This is easiest for users, who simply have to install something like `fileinfo-images-plugin` or
`fileinfo-text-plugin` to get access to the plugin.

Our `fileinfo` will **provide a decorator that will register a callable with a given file extension**. This will "mark"
the callable for the discovery to find and use. 

```python
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

FileInfoHandlerFunction = Callable[[Path], Iterable[str]]  # This is the signature of a decoratable function.
F = TypeVar("F", bound=FileInfoHandlerFunction)  # This is a TypeVar to indicate that we get out what we put in.


def file_type(pattern: str) -> Callable[[F], F]:
    """Decorates a callable to indicate that it handles a certain type.

    Args:
        pattern: Regex pattern of the file extension to match.

    Returns:
        A decorator function that returns the original function, but with additional attributes to mark the function.
    """

    def wrapper(func: F) -> F:
        """Wraps a callable to mark it for a given type."""
        # Add an attribute to the callable that is a set of supported type patterns. If the attribute already exists 
        # and is a set, then just append to the pattern to the existing set.
        LOG.debug("Registering %s to %s", func, pattern)
        if isinstance(getattr(func, "_fileinfo_registered_types", None), set):
            LOG.debug("Adding to list")
            func._fileinfo_registered_types.add(pattern)
        else:
            LOG.debug("Creating new list")
            func._fileinfo_registered_types = {pattern}

        return func

    return wrapper
```

Registered callables are expected to have the following signature:

```python
from collections.abc import Callable, Iterable
from pathlib import Path

# Decorated method function.
Callable[[Path], Iterable[str]]
```

Any exceptions raised by callables will be logged at debug level and otherwise suppressed.

All functions that can respond to a file extension will.

### Plugin Usage

Each 

### Example Usage

```
> python -m fileinfo ./test_files

./test_files/foo.txt
TXT file
123 bytes

./test_files/foo.csv
CSV file
123 bytes
```

## Text plugin

Our `fileinfo-text-plugin` will respond to events for `.txt` files, and expose the following information:

* Identify then by the more user-friendly name "Text file"
* Count the number of lines.
* Count the number of words.

```
> python -m fileinfo ./test_files

./test_files/foo.txt
Text file
123 bytes
3 lines
23 words

./test_files/foo.csv
CSV file
123 bytes
```

## CSV plugin

Our `fileinfo-csv-plugin` will respond to events for `.csv` files, and expose the following information:

* Identify them by the more user-friendly name "Comma-Separated Values file"
* Count the number of columns.
* Count the number of rows.
* Identify if there was an error parsing the file as a CSV, and report 0 for the counts.

```
> python -m fileinfo ./test_files

./test_files/foo.txt
TXT file
123 bytes

./test_files/foo.csv
Comma-Separated Values file
123 bytes
3 columns
4 rows
```
