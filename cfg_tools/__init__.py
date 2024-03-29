import importlib.metadata

from cfg_tools import plugins

from .data_parser import ParsedModel, parse_dict, parse_list, parse_str, register_plugin
from .utils import load_config_files, merge_dicts, parse_args

__version__ = importlib.metadata.version("cfg-tools")

__all__ = [
    "parse_str",
    "parse_list",
    "parse_dict",
    "ParsedModel",
    "plugins",
    "register_plugin",
    "parse_args",
    "merge_dicts",
    "load_config_files",
]
