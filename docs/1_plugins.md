# What is a Plugin?

Sometimes you want to enable the expansion of features in a software, but don't want to modify the software every time 
you want to add functionality. Maybe the new functionality needs to be optional Other times, it may be better to have 
functionality maintained independently. A plugin architecture allows the developer to modularize functionality by
creating a separation between **events** (when something happens) and **response** what happens as a result.

In a plugin architecture, the **Host Application** implements some functionality that the user directly interacts with.
For instance, a web browser provides GUI controls for going backwards, forwards, reloading the page, or clicking links.
These activities generate **events**, or signals that something has happened. **Plugins** can respond to these events, 
performing some activity.

Plugins are designed to be optional (they can be there or not be there, and the host application still works). A host
application need only discover the load the plugins, provide a mechanism to allow plugins to associate themselves with
events, and then fire the events when the action occurs.

```mermaid
graph LR
    user[User]

    host[[Host Application]]
    
    subgraph Events
        event1[/Event 1/]
        event2[/Event 2/]
        event3[/Event 3/]
    end

    subgraph Plugins
        plugin1[[Plugin 1]]
        plugin2[[Plugin 2]]
        plugin3[[Plugin 3]]
    end

    user -- interacts with --> host

    host -- fires --> event1
    host -- fires --> event2
    host -- fires --> event3

    event1 -- responds to --> plugin1

    event2 -- responds to --> plugin1
    event2 -- responds to --> plugin3

    event3 -- responds to --> plugin2
    event3 -- responds to --> plugin3
```
