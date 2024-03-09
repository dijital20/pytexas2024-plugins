# The `__main__` event

To make a Python package runnable, you can add a `__main__.py`. When using `python -m <package name>`, the interpreter
searches for `<package name>`, and then looks for the `__main__.py` in the package, executing it. So, our `fileinfo`
module needs to do the following things:

* Parse the user input.
* Load our handler functions, both from the module itself, and from the plugins.
* Turn the input paths from the user into a list of file paths.
* For each file, we should process it against each matching handler functions to give data to the user.

I like to break each task into a simple function.

## Processing command line input

I like `argparse`. Once you learn its API, it's pretty easy to setup everything from a simple command line interface,
to a complex multi-subcommand interface. It's flexible, and best of all, it is part of the standard library. We'll
start with a function that creates the command line parser, adds options, and then parse the contents of the `sys.argv`
to get a namespace with the options.

```python
{% 
    include "../src/fileinfo/__main__.py" 
    start="# --- START CLI ---"
    end="# --- END CLI ---"
    trailing-newlines=false
%}
```

If the user runs `python -m fileinfo --help`, the output looks something like this:

```plaintext
usage: __main__.py [-h] [--verbose] path [path ...]

Get information on files.

positional arguments:
  path           Paths to search.

options:
  -h, --help     show this help message and exit
  --verbose, -v  Enable verbose output.
```

The output object contains a `path` attribute with a list of the paths passed in, and a `verbose` attribute that will
be a `bool` indicating whether the user wants verbose output.

## Turning paths into a list of file paths

Once we have our input paths, we want to turn them into a list of file paths. The user might give us paths to files or
folders, so we need to handle that. Also note, that the user could have annoyingly passed us paths that intersect,
such as passing us both a parent and child path. To combat this, we're gonna do a few things:

* Use a `set` to capture the file paths. This allows us to filter out duplicates.
* If a path is a path to an existing file, we'll just add it to the list.
* If a path is not a path to an existing file, then we'll assume that it is a directory, and recursively search it using
  `rglob("*")`, and add any paths that are files to the list.
* Return the set as a sorted list. This ensures that the files are in a deterministic order.

```python
{% 
    include "../src/fileinfo/__main__.py" 
    start="# --- START Iterate paths ---"
    end="# --- END Iterate paths ---"
    trailing-newlines=false
%}
```

What should remain is a sorted list of file `Path` objects.

## Processing each file

Now let's define a function to handle each file. The function should take care of iterating through handler functions
and their patterns, checking if the file suffix matches the pattern, and if it does, running the handler against the
`Path` object. We'll add error handling around each handler function, so that a misbehaving handler doesn't crash the
host application.

```python
{% 
    include "../src/fileinfo/__main__.py" 
    start="# --- START File processor ---"
    end="# --- END File processor ---"
    trailing-newlines=false
%}
```

## Tying it all together in a `__main__` block

Now it's time to bring it all together. The `__main__` block will get the command line info, find our handler functions,
take our user-submitted paths and create a sorted list of file paths, and then process each file path against the
handlers.

```python
{% 
    include "../src/fileinfo/__main__.py" 
    start="# --- START main ---"
    end="# --- END main ---"
    trailing-newlines=false
%}
```

And now, we have a functioning tool!