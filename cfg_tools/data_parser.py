from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, model_validator

from cfg_tools.plugins import env_plugin, interpolate_plugin

__plugins: dict[str, Callable[[str, Any], Any]] = {
    "interpolate": interpolate_plugin,
    "env": env_plugin,
}


def execute_parser_plugin(plugin: str, key: str, data: Any):
    callback = __plugins[plugin]
    return callback(key, data)


def register_plugin(name):
    def decorator(func):
        if name not in __plugins:
            __plugins[name] = func
        else:
            raise ValueError(f"plugin {name} already registered")
        return func

    return decorator


_default_plugin = "interpolate"


@dataclass
class ParsingContext:
    in_interpolation: bool = False
    is_escaped: bool = False
    interpolation_key: str = ""
    interpolation_plugin: str = _default_plugin


def parse_str(
    query: str,
    data: Any,
    context: ParsingContext | None = None,
) -> Any:
    if not len(query):
        return ""

    if context is None:
        context = ParsingContext()

    letter, rest = query[0], query[1:]
    match letter:
        case "\\" if not context.is_escaped and not context.in_interpolation:
            return parse_str(
                rest,
                data,
                ParsingContext(
                    context.in_interpolation,
                    is_escaped=True,
                    interpolation_key=context.interpolation_key,
                    interpolation_plugin=context.interpolation_plugin,
                ),
            )
        case "{" if not context.is_escaped:
            return parse_str(
                rest,
                data,
                ParsingContext(
                    in_interpolation=True,
                    is_escaped=False,
                    interpolation_key="",
                    interpolation_plugin=_default_plugin,
                ),
            )
        case ":" if (
            context.in_interpolation
            and context.interpolation_plugin == _default_plugin
            and not context.is_escaped
        ):
            return parse_str(
                rest,
                data,
                ParsingContext(
                    in_interpolation=True,
                    is_escaped=False,
                    interpolation_plugin=context.interpolation_key,
                    interpolation_key="",
                ),
            )
        case "}" if context.in_interpolation and not context.is_escaped:
            interpolated = execute_parser_plugin(
                context.interpolation_plugin, context.interpolation_key, data
            )
            if len(rest):
                interpolated = str(interpolated) + parse_str(
                    rest,
                    data,
                    ParsingContext(
                        in_interpolation=False,
                        is_escaped=False,
                        interpolation_key="",
                        interpolation_plugin=_default_plugin,
                    ),
                )

            return interpolated
        case x if context.in_interpolation:
            return parse_str(
                rest,
                data,
                ParsingContext(
                    in_interpolation=True,
                    is_escaped=False,
                    interpolation_key=context.interpolation_key + x,
                    interpolation_plugin=context.interpolation_plugin,
                ),
            )
        case "{" | "}" | "\\" if context.is_escaped:
            return letter + parse_str(
                rest,
                data,
                ParsingContext(
                    in_interpolation=context.in_interpolation,
                    is_escaped=False,
                    interpolation_key=context.interpolation_key,
                    interpolation_plugin=context.interpolation_plugin,
                ),
            )
        case x if context.is_escaped:
            return (
                "\\"
                + letter
                + parse_str(
                    rest,
                    data,
                    ParsingContext(
                        in_interpolation=context.in_interpolation,
                        is_escaped=False,
                        interpolation_key=context.interpolation_key,
                        interpolation_plugin=context.interpolation_plugin,
                    ),
                )
            )
        case x:
            return letter + parse_str(
                rest,
                data,
                ParsingContext(
                    in_interpolation=False,
                    is_escaped=False,
                    interpolation_key="",
                    interpolation_plugin=context.interpolation_plugin,
                ),
            )


def parse_list(queries: Sequence[Any], data: Any) -> list[Any]:
    new_data: list[Any] = []
    for val in queries:
        if isinstance(val, str) and "{" in val and "}" in val:
            new_data.append(parse_str(val, data))
        elif isinstance(val, dict):
            new_data.append(parse_dict(val, data))
        elif isinstance(val, list):
            new_data.append(parse_list(val, data))
        else:
            new_data.append(val)
    return new_data


def parse_dict(queries: Mapping[str, Any], data: Any) -> dict[str, Any]:
    new_data: dict[str, Any] = {}
    for key, val in queries.items():
        if isinstance(val, str) and "{" in val and "}" in val:
            new_data[key] = parse_str(val, data)
        elif isinstance(val, dict):
            new_data[key] = parse_dict(val, data)
        elif isinstance(val, list):
            new_data[key] = parse_list(val, data)
        else:
            new_data[key] = val
    return new_data


class ParsedModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def interpolate_variables(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return parse_dict(data, data)
        elif isinstance(data, list):
            return parse_list(data, data)
        else:
            return data
