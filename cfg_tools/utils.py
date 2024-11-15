import sys
from pathlib import Path
from typing import Any, Type, TypeVar

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails
from rich import print as rprint
from ruamel.yaml import YAML

from cfg_tools.data_parser import ParsedModel


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


def merge_dicts(a: dict[str, Any], b: dict[str, Any] | None):
    """
    Deep merge two dicts. a will be updated with values in b.
    Example:
        a = {"a": {"b": 1, "c": 3}}
        b = {"a": {"b": 2}}
        merge_dicts(a, b)
        assert a == {"a": {"b": 2, "c": 3}}
    """
    if b is None:
        return
    for k in b.keys():
        if k in a:
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                merge_dicts(a[k], b[k])
            else:
                a[k] = b[k]
        else:
            a[k] = b[k]


def load_config_files(
    path: str | Path,
    load_files: list[str],
    use_cli: bool = True,
    argv: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    config_path = Path(path)
    if not config_path.is_dir():
        raise FileNotFoundError(f"Config path {config_path} does not exist.")

    config_dict: dict[str, Any] = {}
    for file in load_files:
        path_file = config_path / file
        if not path_file.is_file():
            raise FileNotFoundError(f"Config file {path_file} does not exist.")
        with open(path_file, "r") as f:
            merge_dicts(config_dict, yaml.safe_load(f))

    cli_config: dict[str, Any] = {}
    if use_cli:
        cli_config = parse_args(argv)
        merge_dicts(config_dict, cli_config)
    return config_dict, cli_config


def make_missing_dict(loc: list[str | int], val: Any) -> Any:
    if not len(loc):
        return val
    if isinstance(loc[0], str):
        return {loc[0]: make_missing_dict(loc[1:], val)}
    elif loc[0] == 0:
        return [make_missing_dict(loc[1:], val)]


def set_config_dynamically(e: ValidationError, config_dict: dict[str, Any]):
    printed_header = False
    other_errors: list[InitErrorDetails] = []
    ask_should_save = False
    set_config_dynamically = False
    new_vals: list[Any] = []
    for error in e.errors():
        if error["type"] == "missing":
            if not printed_header:
                set_config = input(
                    "Your config is missing some values. Do you want to "
                    "set them dynamically? [Y/n]"
                )
                set_config_dynamically = set_config.lower() in ["y", "yes", ""]
                if not set_config_dynamically:
                    raise e

                printed_header = True

            error_name = ".".join(map(str, error["loc"]))
            rprint(f"[blue]{error_name}[/blue]: ", end="")
            new_val = input()
            new_conf = make_missing_dict(list(error["loc"]), new_val)
            new_vals.append(new_conf)
            merge_dicts(config_dict, new_conf)
            ask_should_save = True
        else:
            init_error = InitErrorDetails(
                type=error["type"],
                loc=error["loc"],
                input=error["input"],
            )
            if "ctx" in error:
                init_error["ctx"] = error["ctx"]
            other_errors.append(init_error)
    return other_errors, config_dict, new_vals, ask_should_save


Model = TypeVar("Model", bound=BaseModel | ParsedModel)


def validate_and_fill_missing(
    config_dict: dict[str, Any], conf_cls: Type[Model], conf_path: Path
) -> Model:
    local_yaml = YAML()
    for _ in range(2):
        try:
            return conf_cls.model_validate(config_dict)
        except ValidationError as e:
            other_errors, config_dict, new_vals, should_save = set_config_dynamically(
                e, config_dict
            )
            if should_save:
                rprint(
                    "Do you want to save the values in "
                    "`[green]config/local.yaml[/green]`? [Y/n]",
                    end="",
                )
                do_save = input()
                if do_save.lower() in ["yes", "y", ""]:
                    local_file = {}
                    if (conf_path / "local.yaml").exists():
                        with open(conf_path / "local.yaml") as f:
                            local_file = local_yaml.load(f)
                    for new_val in new_vals:
                        merge_dicts(local_file, new_val)
                    with open(conf_path / "local.yaml", "w") as f:
                        local_yaml.dump(local_file, f)

            if len(other_errors):
                raise ValidationError.from_exception_data(e.title, other_errors) from e
    raise ValueError("Could not parse config")
