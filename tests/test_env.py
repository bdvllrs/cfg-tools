import os

from cfg_tools import parse_str


def test_env():
    data = {"a": "baz"}
    query = "foo bar {env:HOME}"
    parsed_query = parse_str(query, data)
    home_env = os.getenv("HOME")
    assert parsed_query == f"foo bar {home_env}"


def test_env_default():
    data = {"a": "baz"}
    query = "foo bar {env:_RANDOM_NAMEDFJDHF,test}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar test"
