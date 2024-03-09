# Implementing the Plugins

Implementing the plugins is pretty straightforward. We just need to import the `file_type` decorator from 
`fileinfo.plugins`, and apply it to a function. The function just needs to take a `Path` object and return an iterable
of strings to print to the console, so a generator is good here.

Both functions use the regular expression patterns `"\.txt"` and `"\.csv"` respectively. This means the plugins will 
only respond to files that end in `.txt` and `.csv`. In case you are unfamiliar with regular expressions, `\.` matches a 
literal period, while `.` would match any character.

## The Text Plugin

```python
{% 
    include "../src/fileinfo_text_plugin.py" 
    start="# --- START fileinfo_text_plugin ---"
    end="# --- END fileinfo_text_plugin ---"
    trailing-newlines=false
%}
```

This function simply grabs the file contents as a string. It counts lines by counting the number of substrings by
splitting the content by newlines, and counts words by counting the number of substrings by splitting the content by
spaces.

## The Comma-Separated Value Plugin

```python
{% 
    include "../src/fileinfo_csv_plugin.py" 
    start="# --- START fileinfo_csv_plugin ---"
    end="# --- END fileinfo_csv_plugin ---"
    trailing-newlines=false
%}
```

This function makes use of the `reader` from the `csv` module. It counts rows by counting the number of list elements,
and counts columns by the max of the number of elements in each element (this is so that, if a csv has irregular).
