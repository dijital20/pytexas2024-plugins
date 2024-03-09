# Requirements and Design

## Base Application

We're going to make an application called `fileinfo` to print information about files given a directory. By default, the 
host application will just print information common to any file type... the full path, file type, and size.

### Example Usage

```plaintext
> python -m fileinfo ./test_files

./test_files/foo.txt
TXT file
123 bytes

./test_files/foo.csv
CSV file
123 bytes
```

### Event

Our `fileinfo` will **expose a single event as it passes through each type**. 

Since this is a single event system, I won't worry about creating some sort of eventing or callback system... instead, 
the application will manage this event by iterating over the registered plugins and calling the appropriate plugins 
based on file type.

### Plugin Discovery

Our `fileinfo` will **discover plugins on its own by checking for top-level modules that begin with `fileinfo` and 
end with `plugin`**. This is easiest for users, who simply have to install something like `fileinfo-images-plugin` or
`fileinfo-text-plugin` to get access to the plugin.

Plugins for `fileinfo` **will be a callable that is passed a `Path` object of the file, and will return an iterable of
`str` to print** (that signature is `#!python Callable[[Path], Iterable[str]]`). This will keep plugins simple and easy 
to implement.

**Any exceptions raised by callables will be logged at debug level and otherwise suppressed**.

**All functions that can respond to a file extension will**.

## Text plugin

Our `fileinfo-text-plugin` will respond to events for `.txt` files, and expose the following information:

* Count the number of lines.
* Count the number of words.

```
> python -m fileinfo ./test_files

./test_files/foo.txt
.TXT file
123 bytes
Lines 3
Words 23

./test_files/foo.csv
.CSV file
123 bytes
```

## CSV plugin

Our `fileinfo-csv-plugin` will respond to events for `.csv` files, and expose the following information:

* Count the number of columns.
* Count the number of rows.
* If there was an error parsing the file as a CSV, and report 0 for the counts.

```
> python -m fileinfo ./test_files

./test_files/foo.txt
.TXT file
123 bytes

./test_files/foo.csv
.CSV file
123 bytes
Rows 3
Columns 4
```
