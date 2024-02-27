# cfg-tools
Config tools using pydantic

`parse_str(query: str, data: Any)` will parse a string and execute some
plugins.

in the query, any field of the form:
```python
query = "foo {pluginName:content}"
```
will call the plugin `pluginName` with key "content", and access to the `data` dict.
When no plugin is given, it defaults to the "interpolate" plugin.

# Available plugins
## Interpolate
Replaces content by the content in `data` that it references:
```python
from cfg_tools import parse_str


data = {"a": {"b": ["baz"]}}
query = "foo bar {interpolate:a.b.0}"
parsed_query = parse_str(query, data)
# parsed_query = "foo bar baz"
```
Note that interpolate is the default plugin, so no need to indicate the plugin name.
The following works just as well
```python
from cfg_tools import parse_str


data = {"a": {"b": ["baz"]}}
query = "foo bar {a.b.0}"
parsed_query = parse_str(query, data)
# parsed_query = "foo bar baz"
```
## Env
Replaces the content by `os.environ[content]`. You can also set a default value:
```python
from cfg_tools import parse_str


data = {}
query = "foo bar {env:HOME,/home/default}"
parsed_query = parse_str(query, data)
# parsed_query = "foo bar /home/example"
```

## Add your own plugin
You can register your own plugins:
```python
from cfg_tools import parse_str, register_plugin


@register_plugin("test")
def plugin_test(key: str, data: Mapping[str, Any]) -> str:
    return f"test_{key}"
```
Then, this will work:

```python
data = {}
query = "{test:foo}"
parsed_query = parse_str(query, data)
# parsed_query = "test_foo"
```

## Parse objects
You can also parse lists and dicts with `parse_dict` and `parse_list`.
```python
data = {"a": "foo", "b": "bar"}
queries = ["{a}", "{b}"]
parsed_query = parse_list(queries, data)
# parsed_query = ["foo", "bar"]
```

# Pydantic model
Use `ParsedModel` instead of pydantic's `BaseModel` for your root configuration object
to add some parsing abilities.

```python
from pydantic import BaseModel

from cfg_tools import ParsedModel


# Still use BaseModel
class SubConfig(BaseModel):
    name: str


# Use ParsedModel
class Config(ParsedModel):
    name: str
    other: SubConfig
```
