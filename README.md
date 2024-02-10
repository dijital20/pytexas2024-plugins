# pytexas2024-plugins

This repository contains the content for my PyTexas 2024 talk, "Plugging in with pkgutil, importlib, inspect, and a 
little spit".

## Building Content

This repository using `pdm` for dependency management, and `mkdocs` for document rendering. To use this repository, you
will need:

* Python 3.10+ (I used 3.12 to build this)
* Pdm (`pip install pdm`)

Once the repository is cloned, you can:

```
pdm sync
pdm run mkdocs serve
```

Open the URL that `mkdocs` gives you to view the documentation.

## Running Sample Code

The `fileinfo` sample used in the content is available in `src`. To run it:

```
cd src
pdm run python -m fileinfo <PATH>
```

See the talk content for how to develop plugins for `fileinfo`.
