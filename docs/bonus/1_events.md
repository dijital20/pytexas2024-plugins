# Events

For larger systems, where you have more than one event, you may want to consider creating an event. Unlike other 
languages like C#, Python does not have a native event type, but making one is not hard.

"PubSub" is a common event architecture. Consumers that want to consume an event **subscribe** to the event. When the 
event is fired, it is **published** and sent to each of the consumers.

In Python, this could be really easy.

```python
import logging
from copy import deepcopy
from typing import ParamSpec

LOG = logging.getLogger(__name__)
P = ParamSpec("P")

class Event:
    """Represents an event that can be subscribed to or published."""
    
    def __init__(self, name: str):
        """Prepare an Event for use.

        Args:
            name: Name of the event (used for logging).
        """
        self.name = name
        self.subscribers = set()
    
    def subscribe(self, func: Callable[[P], None]) -> Callable[[P], None]:
        """Subscribe a function to the event.

        Args:
            func: Function to subscribe.

        Returns:
            Function passed in.
        """
        self.subscribers.add(func)
        LOG.info("%s: Subscribed %s", self.name, func)
        return func

    def unsubscribe(self, func: Callable[[P], None]) -> Callable[[P], None]:
        """Unsubscribe a function from the event.

        Args:
            func: Function to unsubscribe.

        Returns:
            Function passed in.
        """
        self.subscribers.remove(func)
        LOG.info("%s: Unsubscribed %s", self.name, func)
        return func

    def publish(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Call each subscriber with a copy of the arguments.
        
        Args:
            args, kwargs: Copies passed to subscribers.
        """
        LOG.debug("Publishing to %d subscribers", len(self.subscribers))
        for subscriber in self.subscribers:
            LOG.debug("Calling %s", subscriber)
            subscriber(*deepcopy(args), **deepcopy(kwargs))
```

This is a very simple implementation, and would work for simple functions (instance methods and class methods would take 
extra work). Your host application needs to do things like this:

```python
from event import Event

on_start = Event("on_start")
on_finish = Event("on_finish")
on_new_file = Event("on_finish")
```

Inside subscriber code, you would need to do something like this:

```python
from pathlib import Path
from events import on_start, on_finish, on_new_file

@on_new_file.subscribe
def process_new_file(path: Path):
    ...

@on_start.subscribe
def setup():
    ...

@on_finish.subscribe
def cleanup():
    ...
```

Here are some mods you might make to this very simple setup...

## Use the event itself as a decorator

What if, instead of using `@on_start.subscribe`, you could use `@on_start`? This can be easily done by implementing the 
`__call__()` method on the event class.

```python
# This code assumes the code above...
class Event:
    """Represents an event that can be subscribed to or published."""

    ...

    def __call__(self, func: Callable[[P], None]) -> Callable[[P], None]:
        """Turns the instance into a decorator."""
        return self.subscribe(func)

    ...
```

Now you can easily use an instance of `Event` as a decorator that will subscribe the decorated function to the event.

## Add error handling around subscribers

In the `Event` class above, any subscriber that raises an error will cause the event to fail, and any future subscribers 
not to be called. To combat this, we may want to update the `publish` code to something more like this:

```python
# This code assumes the code above...
class Event:
    """Represents an event that can be subscribed to or published."""

    ...

    def publish(self, *args, **kwargs):
        """Call each subscriber with a copy of the arguments."""
        LOG.debug("Publishing to %d subscribers", len(self.subscribers))
        for subscriber in self.subscribers:
            LOG.debug("Calling %s", subscriber)
            try:
                subscriber(*deepcopy(args), **deepcopy(kwargs))
            except Exception:
                LOG.error("Error calling %s", subscriber)

    ...
```

If you have Python 3.11 and above, and feel squeamish about simply handling these exceptions, how about capturing them 
and raising them as an [exception group](https://docs.python.org/3/library/exceptions.html#exception-groups) with code 
like the following:

```python
# This code assumes the code above...
class Event:
    """Represents an event that can be subscribed to or published."""

    ...

    def publish(self, *args, **kwargs):
        """Call each subscriber with a copy of the arguments."""
        exceptions = []
        LOG.debug("Publishing to %d subscribers", len(self.subscribers))
        for subscriber in self.subscribers:
            LOG.debug("Calling %s", subscriber)
            try:
                subscriber(*deepcopy(args), **deepcopy(kwargs))
            except Exception as e:
                LOG.error("Error calling %s", subscriber)
                exceptions.append(e)

        if exceptions:
            raise ExceptionGroup(
                f"{len(exceptions)} subscribers raised exceptions.", 
                exceptions,
            )
    ...
```

## Use an "arguments dataclass" to make passing arguments easier.

The class above assumes that all subscribers support a given signature. This carries a documentation requirement for
the host application developer and a knowledge requirement for the subscriber developer. Also, the `deepcopy` of the
`args` and `kwargs` is clunky. One way we could fix this up is to create a dataclass for the arguments.

First, let's update our `Event` implementation to take and pass the class:

```python
class Event:
    """Represents an event that can be subscribed to or published."""
    
    def __init__(self, name: str, arg_class: type):
        """Prepare an Event for use.

        Args:
            name: Name of the event (used for logging).
        """
        self.name = name
        self.arg_class = arg_class
        self.subscribers = set()
    
    ...

    def publish(self, *args, **kwargs):
        """Call each subscriber with a copy of the arguments."""
        event_args = self.arg_class(*args, **kwargs)
        
        LOG.debug("Publishing to %d subscribers", len(self.subscribers))
        for subscriber in self.subscribers:
            LOG.debug("Calling %s", subscriber)
            subscriber(deepcopy(event_args))

    ...
```

Then we change our usage something like this:

```python
from dataclasses import dataclass
from event import Event

@dataclass(frozen=True)
class GenericArgs:
    """Args for generic events with no data."""

@dataclass(frozen=True)
class NewFileArgs:
    """Args for new path events."""
    path: Path


on_start = Event("on_start", GenericArgs)
on_finish = Event("on_finish", GenericArgs)
on_new_file = Event("on_finish", NewFileArgs)
```

This eases the problem in 2 ways:

1. We only try to squeeze the call-time `args` and `kwargs` one time, when `publish` is called. If you are diligent 
   about using frozen dataclasses, then you can also remove the `deepcopy` call since the instance won't be mutable.
2. Subscriber functions only need to take a single argument, and they can know the class and arguments up front since
   they are defined.

## Execute subscribers asynchronously

You can make subscribers `async` functions, or call the functions in `Thread` instances, so that they run 
asynchronously. This can potentially speed things up, at the cost of complicating debugging. Just make the appropriate
changes in `publish` (to call things asynchronously) and optionally `subscribe` (to check if the function is 
asynchronous, if that's required).

Depending on how complex you want to get, you might also implement some sort of watchdog and timeout, so that you kill
subscribers that take too long. If you do something aggressive like this though, make sure you document it for 
developers!