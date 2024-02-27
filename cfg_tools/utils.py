import sys
from typing import Any


def parse_args(argv: list[str] | None = None) -> dict[str, Any]:
    """
    Parse argument list into a dictionary.
    Nested dict can be provided using dot notation:
        "a.b=1" will create {"a": {"b": 1}}.
    All keys must have a value and be separated by a "="
    """
    if argv is None:
        argv = sys.argv[1:]

    config: dict[str, Any] = {}
    for arg in argv:
        idx = arg.find("=")
        if idx == -1:
            raise ValueError(f'{arg} has no value. Use "{arg}=value" instead.')
        keys = arg[0:idx].split(".")
        value = arg[idx + 1 :]
        c = config
        for key in keys[:-1]:
            if key not in c.keys():
                c[key] = {}
            c = c[key]
        c[keys[-1]] = value
    return config


def merge_dicts(a: dict[str, Any], b: dict[str, Any]):
    """
    Deep merge two dicts. a will be updated with values in b.
    Example:
        a = {"a": {"b": 1, "c": 3}}
        b = {"a": {"b": 2}}
        merge_dicts(a, b)
        assert a == {"a": {"b": 2, "c": 3}}
    """
    for k in b.keys():
        if k in a:
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                merge_dicts(a[k], b[k])
            else:
                a[k] = b[k]
        else:
            a[k] = b[k]
