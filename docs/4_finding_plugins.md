# Discovering and Loading Plugins

## Finding plugins

In order to discover plugins, we need to be able to do the following:

1. **Get a list of all of the accessible Python modules.** These could be provided by the standard library, installed, or
  just modules in the path.
2. **For each module name we find, import that module, so we can search its local objects.**
3. **If the module has submodules, we might want to crawl those.** This could give the plugin developer more freedom to
  structure the plugins wherever in the code makes sense.
4. **Iterate through all of the objects in the module's namespace to find plugins.** In this case, we need to find 
  functions that our decorator has "marked" as a plugin function.

---

### Finding packages/modules using `pkgutil`

First off, we need to be able to iterate through the installed packages and modules. The `pkgutil` module provides a
couple of good functions for this.

#### `pkgutil.walk_packages`: Walking into the structure

The `pkgutil.walk_packages` allows you to iterate through every accessible package and module **by importing every 
package**. This is good in that it will find every module and submodule, but bad in that some modules actually execute 
behavior **_on import_**, which can cause issues on your discovery. 

An example of an adverse effect is the `test_gdb` module, which tries to find and execute unit tests on import. This 
would at best kill your script right there, and at worst, begin executing unit tests.

```python
>>> import pkgutil
>>> list(pkgutil.walk_packages())
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py", line 93, in walk_packages
    yield from walk_packages(path, info.name+'.', onerror)
  File "/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py", line 78, in walk_packages
    __import__(info.name)
  File "/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/test/test_gdb/__init__.py", line 22, in <module>
    raise unittest.SkipTest("test_gdb only works on source builds at the moment.")
unittest.case.SkipTest: test_gdb only works on source builds at the moment.
```

So if we can't use `pkgutil.walk_packages`, what can we do?

#### `pkgutil.iter_modules`: Just skimming the top

The `pkgutil.iter_modules` allows you to iterate through top-level modules/packages **without importing them**. This 
means that we can find all of the top-level packages and modules, but submodules or packages (packages or modules inside
a top-level package) will not be visible. In order to get these, the interpreter needs to import the package. Each 
package/module will be exposed as a string name, so it should be easy to search for names that match a predefined
pattern. Once you have the names, now you need to import... and that's where the next library comes in.

---

### Importing a module given its name as a string using `importlib`

Normally you would import a module or package like this:

```python
>>> import os.path
```

But what if you have `"os.path"`? Well, that's where `importlib.import_module` comes in. This means you can do something
like this:

```python
>>> import importlib
>>> module_name = "os.path"
>>> importlib.import_module(module_name)
<module 'posixpath' (frozen)>
```

This would give you the module as an object. From there, you need to filter through its members to find plugin functions
and to do that, you might want to use `inspect`.

---

### Searching the module for plugins using `inspect`

Once you have imported a module, you can use `inspect` to filter its namespace. The `inspect` library provides functions
for filtering through objects, including a bunch of useful "predicate functions" (Functions that take the object and
return `True` if they are the droids you're looking for, or `False` if not).

We can use `inspect.getmembers` to get all of the members of the module. We can also optionally specify a predicate 
function, and `getmembers` will only return the members where the predicate function returns `True`.

Since we're digging for functions, we will use the `inspect.isfunction` predicate function.

---

## Putting it all together

So, let's work backwards. 

### Step 1: Identify a plugin function

Our decorator works by adding an attribute containing a set of regex patterns for the files
that the function supports, so let's start by creating a predicate function to define the function. Remember that
`ATTR_NAME` constant we defined previously? This code will use that.

```python
{% 
    include "../src/fileinfo/plugins.py" 
    start="# --- START Predicate ---"
    end="# --- END Predicate ---"
    trailing-newlines=false
%}
```

Our predicate function here should be useful by `inspect.getmembers` for finding functions with our attribute. 

### Step 2: Load plugin functions from a module given its name

Next, we'll want to load and search a module given its name. To do this, we'll create another function to import the 
module using `importlib.import_module` and `inspect.getmembers` to search. We'll do some exception handling around the 
import, just in case there is bad code in there, so that the host application doesn't crash.

```python
{% 
    include "../src/fileinfo/plugins.py" 
    start="# --- START Function Finder ---"
    end="# --- END Function Finder ---"
    trailing-newlines=false
%}
```

### Step 3: Find modules that match our plugin name and search them for plugin functions

Now that we can load a module given its name, we should go find modules to load. This is the top level of our plugin
search. This will use `pkgutil.iter_modules` to iterate through the top level modules, looking for ones that start with 
`fileinfo` and end with `plugin`. Once we have those, we will use `pkgutil.walk_packages` to walk the packages and
modules inside, and pass each module we find to our function above to find.

```python
{% 
    include "../src/fileinfo/plugins.py" 
    start="# --- START Plugin Finder ---"
    end="# --- END Plugin Finder ---"
    trailing-newlines=false
%}
```

The end result of all of this is a list of 2-element tuples; the first element is the regex that the file suffix needs
to match, and the second element is the corresponding plugin function. Our main block code can load the plugins,
and then for each file it encounters, run plugin functions for that file type.

Note that we added our default handler to the top of the list with this line:

```python
found_handlers += _find_functions_in_module(__name__)
```

Now that our plugins are loaded, let's build our plugins, and then put the last of this together with main block code.