from collections.abc import Mapping, Sequence
from typing import Any


def interpolate_plugin(
    dotlist: str,
    data: Any,
) -> Any:
    return _interpolate(dotlist.split("."), data, dotlist)


def _interpolate(
    dotlist: Sequence[str],
    data: Any,
    full_key: str,
) -> Any:
    if len(dotlist) == 0:
        raise KeyError(f"{full_key} cannot be interpolated because does not exist.")

    key = dotlist[0]
    if isinstance(data, list):
        if not dotlist[0].isdigit():
            raise KeyError(f"{dotlist[0]} should be an int when data is a sequence")

    if len(dotlist) == 1 and isinstance(data, Mapping):
        return data[key]
    elif len(dotlist) == 1 and isinstance(data, Sequence):
        return data[int(key)]

    elif isinstance(data, Mapping):
        return _interpolate(dotlist[1:], data[key], full_key)
    elif isinstance(data, list):
        return _interpolate(dotlist[1:], data[int(key)], full_key)
    raise ValueError("Provided data cannot be interpolated")
