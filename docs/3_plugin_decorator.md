# Designing Plugins

After requirements, it's good to sit down and think through the design. There are many ways to solve any given problem,
but the right way is the one that accomplishes the most of your requirements, while leaving the most room and
flexibility to grow.

## Picking an approach

I want to be able to find plugins, so I needed to give thought on how a plugin developer should approach creating one.
Here are a few possible approaches:

**Spoiler alert: I'm going with a callable decorator here. Let's see what some of my other options were...**

### Plugin Classes

I could create a plugin class. Classes are good because they have their own scope (instance), can be easily discovered
via hierarchy, and can be mutated via subclassing. This is my favored approach for more complex products (where there
may be more numerous and diverse kinds of events) or when I think plugins may want to manage a state. Sure, a function
can manage the state in global, but it's messy... classes are much cleaner.

To do this, I would probably build an **Abstract Base Class (ABC)** that defines the interface of a plugin. An ABC is
a great way to give developers feedback on how their plugin classes should be structured. In most approaches, I have 
established methods for the events which are automatically called, so the ABC should define those methods and their 
signatures.

```python
import logging
from abc import ABC, abstractmethod

# Abstract Base Class to define the interface for all plugins. An plugin would 
# need to implement this class, and the ABC ensures that all plugins implement 
# the required methods that the host application will call.
class PluginInterface(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def on_setup(self, command_line_options: dict[str, str]):
        pass

    @abstractmethod
    def on_my_event(self, item: str):
        pass

    @abstractmethod
    def on_cleanup(self):
        pass
```

Then I'd create a concrete implementation, which implements the ABC, but on its own, doesn't do anything.

```python
# A concrete implementation suitable for subclassing, which also provides a 
# logger at the self._log attribute.
# 
# This would allow a plugin author to subclass this class, and only override the
# methods they need to. This class already implements the interface, so 
# subclasses of it meet the needs "for free".
class Plugin(PluginInterface):
    def __init__(self):
        self._log = logging.getLogger(
            f"{__module__.__name__}.{type(self).__name__}.{id(self)}"
        )

    def on_setup(self, command_line_options: dict[str, str]):
        self._log.debug("on_setup running from %s", self)

    def on_my_event(self, item: str):
        self._log.debug("on_my_event running from %s with item=%r", self, item)

    def on_cleanup(self):
        self._log.debug("on_cleanup running from %s", self)
```

The discovery mechanism just needs to be able to find subclasses of the plugin ABC that aren't the concrete class, and 
then instantiate those. Assuming the developer followed good SOLID principles and the ABC is doing its thing, any 
subclasses should work.

On event, I'd just need to iterate through the loaded plugins, calling the appropriate event method.

### Specifically named functions

Similar to the way `pytest` does things, I could just specify special "magic" functions. These would need to have a 
specific name, signature, and return type. Discovery is as simple as looking for modules containing functions of the
right name. If you insist on things like type hints, you might also add checks that the signature is compatible and
that the return type is consistent.

You have the same issue with functions above... any state would need to be handled in the global scope of the module
which can get messy, or instantiate a class to handle that. Generally, I am not a fan of instances of a class being 
created merely by importing a module, but it is a way to keep the scope clean.

It's also hard to apply additional metadata. For instance, in this case, the host application needs to know what kinds
of files the plugin can apply to. This could be covered in the module's global scope, but that is, again, messy. Or I
could set the plugins to be called for all files, and leave it to the developer to handle exiting if it's not a type
of file that it can handle. There are pros and cons to this, but I feel like the less code plugin developers have to
write, the better.

This could work much better the way `pytest` uses it, where plugins aren't discovered by combing the codebase, but 
instead, present in the things you are running. In that case, these are less plugins, and more hooks into the host
application.

### Entry Points

Entry points are something that has only recently come to my attention. There's definitely benefits, such as giving the
tools to the plugin developer to control exposing their plugins instead of the host application having to go find them.

More details on how this works can be found here:

* [Creating and discovering plugins - packaging.python.org](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
* [Entry Points - setuptools.pypa.io](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)

The host application starts by defining a name (let's say `fileinfo` here) and the signature that a plugin has.

The plugin developer would create a plugin function, say `handle_csv`, in the `fileinfo_csv` module. The plugin 
developer would then have to add an entry to the `pyproject.toml` like this:

```toml
[project.entry-points.'fileinfo.plugins']
csv = 'fileinfo_csv:handle_csv'
```

The host application can find these by:

```python
from importlib.metadata import find_entrypoints

entry_points = find_entrypoints(group='fileinfo.plugins')
```

This mechanism puts the power and responsibility in the plugin developer's hands to "tell" the host application what
plugins you provide. This provides a pro in allowing the plugin developer to control what loads and does not load,
at the cost of the plugin developer having to explicitly define this.

For this project though, let's get a little more dynamic.

### Decorator

Decorators are awesome. In this case, a parameterized decorator could take the metadata that I want to keep track of,
and attach it to the callable object by way of an attribute. Discovery is a matter of looking for callable that has
the attribute that I need, and parse the information out of it.

For something this simple, this seems to be a good way to go.

---

## The Decorator

So we want a decorator to decorate callable objects which will respond to each file that matches a regular expression 
that is provided to the decorator. This allows the plugin developer to control which functions are called for which file 
types.

```python
{% 
    include "../src/fileinfo/plugins.py" 
    start="# --- START Decorator ---"
    end="# --- END Decorator ---"
    trailing-newlines=false
%}
```

This decorator works by taking in a callable, and either adds a new `_fileinfo_registered_type` attribute with a new
set of regex patterns or appends to an existing set if the attribute exists and is a set; and then returns the original
callable. This allows us to "tag" the callable to a specific file type. This also allows us to use the decorator on
a function more than once to register it to more than 1 file type pattern.

## Applying the Decorator

Now that we have a decorator, we can use it to apply the default case, and see it in action.

```python
{%
    include "../src/fileinfo/plugins.py"
    start="# --- START Default handler ---"
    end="# --- END Default handler ---"
    trailing-newlines=false
%}
```

We assigned this function to the regular expression `".*"` which will match any string, even an empty one. This means
that this function will be called for every file.
