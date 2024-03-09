# Implementing the Plugins

Implementing the plugins is pretty straightforward.

## The Text Plugin

```python
{% 
    include "../src/fileinfo_text_plugin.py" 
    start="# --- START fileinfo_text_plugin ---"
    end="# --- END fileinfo_text_plugin ---"
    trailing-newlines=false
%}
```

## The Comma-Separated Value Plugin

```python
{% 
    include "../src/fileinfo_csv_plugin.py" 
    start="# --- START fileinfo_csv_plugin ---"
    end="# --- END fileinfo_csv_plugin ---"
    trailing-newlines=false
%}
```