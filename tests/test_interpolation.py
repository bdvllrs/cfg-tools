import pytest

from cfg_tools import parse_str


def test_interpolation():
    data = {"a": "baz"}
    query = "foo bar #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_no_interpolation():
    data = {"a": "baz"}
    query = "foo bar {a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar {a}"


def test_interpolation_several():
    data = {"a": "baz", "b": "test"}
    query = "foo bar #{a} #{b}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz test"


def test_interpolation_several_same():
    data = {"a": "baz"}
    query = "foo bar #{a}#{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar bazbaz"


def test_interpolation_int():
    data = {"a": "1"}
    query = "foo bar #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar 1"


def test_interpolation_nested():
    data = {"a": {"b": "baz"}}
    query = "foo bar #{a.b}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolation_escaped():
    data = {"a": "baz"}
    query = "foo bar \\#{test} #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar #{test} baz"


def test_interpolation_escaped_in_interpolation():
    data = {"\\a": "baz"}
    query = "foo bar #{\\a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolation_escaped_in_interpolation_2():
    data = {"a}": "baz"}
    query = "foo bar #{a\\}}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolation_other():
    data = {"a": "baz"}
    query = "foo bar \\n #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar \\n baz"


def test_interpolation_other_2():
    data = {"a": "baz"}
    query = "foo bar \\\\\\#{test} #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar \\#{test} baz"


def test_interpolation_other_3():
    data = {"a": "baz"}
    query = "foo bar \\\\#{a} #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar \\baz baz"


def test_interpolation_other_4():
    data = {"a": "baz"}
    query = "foo bar \\\\a #{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar \\a baz"


def test_interpolation_missing():
    data = {"a": "baz"}
    query = "foo bar #{b}"
    with pytest.raises(KeyError):
        parse_str(query, data)


def test_interpolation_missing_nested():
    data = {"a": {"b": "baz"}}
    query = "foo bar #{b}"
    with pytest.raises(KeyError):
        parse_str(query, data)


def test_interpolation_missing_nested_2():
    data = {"a": {"b": "baz"}}
    query = "foo bar #{a.c}"
    with pytest.raises(KeyError):
        parse_str(query, data)


def test_interpolate_sequence():
    data = ["baz"]
    query = "foo bar #{0}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolate_sequence_2():
    data = ["test", "baz"]
    query = "foo bar #{1}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolate_sequence_error():
    data = ["baz"]
    query = "foo bar #{1}"
    with pytest.raises(IndexError):
        parse_str(query, data)


def test_interpolate_sequence_error_2():
    data = ["baz"]
    query = "foo bar #{a}"
    with pytest.raises(KeyError):
        parse_str(query, data)


def test_interpolate_nested_sequence():
    data = {"a": {"b": ["test", "baz"]}}
    query = "foo bar #{a.b.1}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_interpolate_nested_sequence_2():
    data = {"a": ["test", {"b": "baz"}]}
    query = "foo bar #{a.1.b}"
    parsed_query = parse_str(query, data)
    assert parsed_query == "foo bar baz"


def test_parsed_query_change_type():
    data = {"a": 1}
    query = "#{a}"
    parsed_query = parse_str(query, data)
    assert parsed_query == 1
