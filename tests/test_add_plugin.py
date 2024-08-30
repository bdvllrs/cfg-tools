from typing import Any

from cfg_tools import parse_str, register_plugin


@register_plugin("test")
def plugin_test(key: str, _) -> str:
    return f"test_{key}"


def test_register_plugin():
    data: dict[str, Any] = {}
    query = "#{test:foo}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "test_foo"
