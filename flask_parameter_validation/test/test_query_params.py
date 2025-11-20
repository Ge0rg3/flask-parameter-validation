# String Validation
import sys
import datetime
import json
import uuid
from typing import Type, List, Optional

from flask_parameter_validation.test.enums import Binary, Fruits


def list_assertion_helper(length: int, list_children_type: Type, expected_list: List, tested_list,
                          expected_call: Optional[str] = None):
    for i in range(length):
        assert type(tested_list[i]) is list_children_type
        if expected_call is not None:
            fn = getattr(expected_list[i], expected_call)
            assert fn() == tested_list[i]
        else:
            assert expected_list[i] == tested_list[i]


def test_required_str(client):
    url = "/query/str/required"
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_required_str_decorator(client):
    url = "/query/str/decorator/required"
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_required_str_async_decorator(client):
    url = "/query/str/async_decorator/required"
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_str(client):
    url = "/query/str/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"


def test_optional_str_decorator(client):
    url = "/query/str/decorator/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"


def test_optional_str_async_decorator(client):
    url = "/query/str/async_decorator/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present input yields input value
    r = client.get(url, query_string={"v": "v"})
    assert "v" in r.json
    assert r.json["v"] == "v"


def test_optional_str_blank_none_unset(client, app):
    url = "/query/str/blank_none/unset"
    # Test that FPV_BLANK_NONE returns empty string when False
    app.config.update({"FPV_BLANK_NONE": False})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that FPV_BLANK_NONE returns None when True
    app.config.update({"FPV_BLANK_NONE": True})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that FPV_BLANK_NONE runs as False by default
    app.config.pop("FPV_BLANK_NONE", None)
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""


def test_optional_str_blank_none_true(client, app):
    url = "/query/str/blank_none/true"
    # Test that FPV_BLANK_NONE of False can be overridden to True per-route
    app.config.update({"FPV_BLANK_NONE": False})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that FPV_BLANK_NONE of True can be 'overridden' to True per-route
    app.config.update({"FPV_BLANK_NONE": True})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that unset FPV_BLANK_NONE can be overridden to True per-route
    app.config.pop("FPV_BLANK_NONE", None)
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] is None


def test_optional_str_blank_none_false(client, app):
    url = "/query/str/blank_none/false"
    # Test that FPV_BLANK_NONE of False can be 'overridden' to False per-route
    app.config.update({"FPV_BLANK_NONE": False})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that FPV_BLANK_NONE of True can be overridden to False per-route
    app.config.update({"FPV_BLANK_NONE": True})
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that unset FPV_BLANK_NONE can be 'overridden' to False per-route
    app.config.pop("FPV_BLANK_NONE", None)
    r = client.get(f"{url}", query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""


def test_str_default(client):
    url = "/query/str/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "opt" in r.json
    assert r.json["opt"] == "optional"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "not_optional"
    # Test that present input for required and optional yields input values
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "opt" in r.json
    assert r.json["opt"] == "a"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "b"


def test_str_default_decorator(client):
    url = "/query/str/decorator/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "opt" in r.json
    assert r.json["opt"] == "optional"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "not_optional"
    # Test that present input for required and optional yields input values
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "opt" in r.json
    assert r.json["opt"] == "a"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "b"


def test_str_default_async_decorator(client):
    url = "/query/str/async_decorator/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "opt" in r.json
    assert r.json["opt"] == "optional"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "not_optional"
    # Test that present input for required and optional yields input values
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "opt" in r.json
    assert r.json["opt"] == "a"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "b"


def test_str_min_str_length(client):
    url = "/query/str/min_str_length"
    # Test that below minimum yields error
    r = client.get(url, query_string={"v": ""})
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above minimum yields input
    r = client.get(url, query_string={"v": "aaa"})
    assert "v" in r.json
    assert r.json["v"] == "aaa"


def test_str_min_str_length_decorator(client):
    url = "/query/str/decorator/min_str_length"
    # Test that below minimum yields error
    r = client.get(url, query_string={"v": ""})
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above minimum yields input
    r = client.get(url, query_string={"v": "aaa"})
    assert "v" in r.json
    assert r.json["v"] == "aaa"


def test_str_min_str_length_async_decorator(client):
    url = "/query/str/async_decorator/min_str_length"
    # Test that below minimum yields error
    r = client.get(url, query_string={"v": ""})
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above minimum yields input
    r = client.get(url, query_string={"v": "aaa"})
    assert "v" in r.json
    assert r.json["v"] == "aaa"


def test_str_max_str_length(client):
    url = "/query/str/max_str_length"
    # Test that below maximum yields input
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that at maximum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above maximum yields error
    r = client.get(url, query_string={"v": "aaa"})
    assert "error" in r.json


def test_str_max_str_length_decorator(client):
    url = "/query/str/decorator/max_str_length"
    # Test that below maximum yields input
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that at maximum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above maximum yields error
    r = client.get(url, query_string={"v": "aaa"})
    assert "error" in r.json


def test_str_max_str_length_async_decorator(client):
    url = "/query/str/async_decorator/max_str_length"
    # Test that below maximum yields input
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that at maximum yields input
    r = client.get(url, query_string={"v": "aa"})
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above maximum yields error
    r = client.get(url, query_string={"v": "aaa"})
    assert "error" in r.json


def test_str_whitelist(client):
    url = "/query/str/whitelist"
    # Test that input within whitelist yields input
    r = client.get(url, query_string={"v": "ABC123"})
    assert "v" in r.json
    assert r.json["v"] == "ABC123"
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of whitelist yields error
    r = client.get(url, query_string={"v": "def456"})
    assert "error" in r.json


def test_str_whitelist_decorator(client):
    url = "/query/str/decorator/whitelist"
    # Test that input within whitelist yields input
    r = client.get(url, query_string={"v": "ABC123"})
    assert "v" in r.json
    assert r.json["v"] == "ABC123"
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of whitelist yields error
    r = client.get(url, query_string={"v": "def456"})
    assert "error" in r.json


def test_str_whitelist_async_decorator(client):
    url = "/query/str/async_decorator/whitelist"
    # Test that input within whitelist yields input
    r = client.get(url, query_string={"v": "ABC123"})
    assert "v" in r.json
    assert r.json["v"] == "ABC123"
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of whitelist yields error
    r = client.get(url, query_string={"v": "def456"})
    assert "error" in r.json


def test_str_blacklist(client):
    url = "/query/str/blacklist"
    # Test that input within blacklist yields error
    r = client.get(url, query_string={"v": "ABC123"})
    assert "error" in r.json
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of blacklist yields input
    r = client.get(url, query_string={"v": "def456"})
    assert "v" in r.json
    assert r.json["v"] == "def456"


def test_str_blacklist_decorator(client):
    url = "/query/str/decorator/blacklist"
    # Test that input within blacklist yields error
    r = client.get(url, query_string={"v": "ABC123"})
    assert "error" in r.json
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of blacklist yields input
    r = client.get(url, query_string={"v": "def456"})
    assert "v" in r.json
    assert r.json["v"] == "def456"


def test_str_blacklist_async_decorator(client):
    url = "/query/str/async_decorator/blacklist"
    # Test that input within blacklist yields error
    r = client.get(url, query_string={"v": "ABC123"})
    assert "error" in r.json
    # Test that mixed input yields error
    r = client.get(url, query_string={"v": "abc123"})
    assert "error" in r.json
    # Test that input outside of blacklist yields input
    r = client.get(url, query_string={"v": "def456"})
    assert "v" in r.json
    assert r.json["v"] == "def456"


def test_str_pattern(client):
    url = "/query/str/pattern"
    # Test that input matching pattern yields input
    r = client.get(url, query_string={"v": "AbC123"})
    assert "v" in r.json
    assert r.json["v"] == "AbC123"
    # Test that input failing pattern yields error
    r = client.get(url, query_string={"v": "123ABC"})
    assert "error" in r.json


def test_str_pattern_decorator(client):
    url = "/query/str/decorator/pattern"
    # Test that input matching pattern yields input
    r = client.get(url, query_string={"v": "AbC123"})
    assert "v" in r.json
    assert r.json["v"] == "AbC123"
    # Test that input failing pattern yields error
    r = client.get(url, query_string={"v": "123ABC"})
    assert "error" in r.json


def test_str_pattern_async_decorator(client):
    url = "/query/str/async_decorator/pattern"
    # Test that input matching pattern yields input
    r = client.get(url, query_string={"v": "AbC123"})
    assert "v" in r.json
    assert r.json["v"] == "AbC123"
    # Test that input failing pattern yields error
    r = client.get(url, query_string={"v": "123ABC"})
    assert "error" in r.json


def test_str_func(client):
    url = "/query/str/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": "123"})
    assert "v" in r.json
    assert r.json["v"] == "123"
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": "abc"})
    assert "error" in r.json


def test_str_func_decorator(client):
    url = "/query/str/decorator/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": "123"})
    assert "v" in r.json
    assert r.json["v"] == "123"
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": "abc"})
    assert "error" in r.json


def test_str_func_async_decorator(client):
    url = "/query/str/async_decorator/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": "123"})
    assert "v" in r.json
    assert r.json["v"] == "123"
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": "abc"})
    assert "error" in r.json


def test_str_alias(client):
    url = "/query/str/alias"
    # Test that original name yields error
    r = client.get(url, query_string={"value": "abc"})
    assert "error" in r.json
    # Test that alias yields input
    r = client.get(url, query_string={"v": "abc"})
    assert "value" in r.json
    assert r.json["value"] == "abc"


def test_str_alias_decorator(client):
    url = "/query/str/decorator/alias"
    # Test that original name yields error
    r = client.get(url, query_string={"value": "abc"})
    assert "error" in r.json
    # Test that alias yields input
    r = client.get(url, query_string={"v": "abc"})
    assert "value" in r.json
    assert r.json["value"] == "abc"


def test_str_alias_async_decorator(client):
    url = "/query/str/async_decorator/alias"
    # Test that original name yields error
    r = client.get(url, query_string={"value": "abc"})
    assert "error" in r.json
    # Test that alias yields input
    r = client.get(url, query_string={"v": "abc"})
    assert "value" in r.json
    assert r.json["value"] == "abc"


# Int Validation
def test_required_int(client):
    url = "/query/int/required"
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_int_decorator(client):
    url = "/query/int/decorator/required"
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_int_async_decorator(client):
    url = "/query/int/async_decorator/required"
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_int(client):
    url = "/query/int/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that present non-int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_int_default(client):
    url = "/query/int/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 1
    assert "opt" in r.json
    assert r.json["opt"] == 2
    # Test that present int input for required and optional yields input values
    r = client.get(url, query_string={"opt": 3, "n_opt": 4})
    assert "opt" in r.json
    assert r.json["opt"] == 3
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 4
    # Test that present non-int input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_int_min_int(client):
    url = "/query/int/min_int"
    # Test that below minimum yields error
    r = client.get(url, query_string={"v": -1})
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(url, query_string={"v": 0})
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above minimum yields input
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1


def test_int_max_int(client):
    url = "/query/int/max_int"
    # Test that below maximum yields input
    r = client.get(url, query_string={"v": -1})
    assert "v" in r.json
    assert r.json["v"] == -1
    # Test that at maximum yields input
    r = client.get(url, query_string={"v": 0})
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above maximum yields error
    r = client.get(url, query_string={"v": 1})
    assert "error" in r.json


def test_int_func(client):
    url = "/query/int/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": 8})
    assert "v" in r.json
    assert r.json["v"] == 8
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": 9})
    assert "error" in r.json


# Bool Validation
def test_required_bool(client):
    url = "/query/bool/required"
    # Test that present lowercase bool input yields input value
    r = client.get(url, query_string={"v": "true"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present mixed-case bool input yields input value
    r = client.get(url, query_string={"v": "TruE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present uppercase bool input yields input value
    r = client.get(url, query_string={"v": "TRUE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_bool_decorator(client):
    url = "/query/bool/decorator/required"
    # Test that present lowercase bool input yields input value
    r = client.get(url, query_string={"v": "true"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present mixed-case bool input yields input value
    r = client.get(url, query_string={"v": "TruE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present uppercase bool input yields input value
    r = client.get(url, query_string={"v": "TRUE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_bool_async_decorator(client):
    url = "/query/bool/async_decorator/required"
    # Test that present lowercase bool input yields input value
    r = client.get(url, query_string={"v": "true"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present mixed-case bool input yields input value
    r = client.get(url, query_string={"v": "TruE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present uppercase bool input yields input value
    r = client.get(url, query_string={"v": "TRUE"})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_bool(client):
    url = "/query/bool/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present bool input yields input value
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present non-bool input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_bool_default(client):
    url = "/query/bool/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] is False
    assert "opt" in r.json
    assert r.json["opt"] is True
    # Test that present bool input for required and optional yields input values
    r = client.get(url, query_string={"opt": False, "n_opt": True})
    assert "opt" in r.json
    assert r.json["opt"] is False
    assert "n_opt" in r.json
    assert r.json["n_opt"] is True
    # Test that present non-bool input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_bool_func(client):
    url = "/query/bool/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": False})
    assert "error" in r.json


# Float Validation
def test_required_float(client):
    url = "/query/float/required"
    # Test that present float input yields input value
    r = client.get(url, query_string={"v": 1.2})
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present int input yields float(input) value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1.0
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-float input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_float_decorator(client):
    url = "/query/float/decorator/required"
    # Test that present float input yields input value
    r = client.get(url, query_string={"v": 1.2})
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present int input yields float(input) value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1.0
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-float input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_float_async_decorator(client):
    url = "/query/float/async_decorator/required"
    # Test that present float input yields input value
    r = client.get(url, query_string={"v": 1.2})
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present int input yields float(input) value
    r = client.get(url, query_string={"v": 1})
    assert "v" in r.json
    assert r.json["v"] == 1.0
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-float input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_float(client):
    url = "/query/float/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present float input yields input value
    r = client.get(url, query_string={"v": 1.2})
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present non-float input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_float_default(client):
    url = "/query/float/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 2.3
    assert "opt" in r.json
    assert r.json["opt"] == 3.4
    # Test that present float input for required and optional yields input values
    r = client.get(url, query_string={"opt": 4.5, "n_opt": 5.6})
    assert "opt" in r.json
    assert r.json["opt"] == 4.5
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 5.6
    # Test that present non-float input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_float_func(client):
    url = "/query/float/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": 3.141592})
    assert "v" in r.json
    assert r.json["v"] == 3.141592
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": 3.15})
    assert "error" in r.json


# datetime Validation
def test_required_datetime(client):
    url = "/query/datetime/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.datetime(2024, 2, 9, 3, 47, tzinfo=datetime.timezone.utc)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_datetime_decorator(client):
    url = "/query/datetime/decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.datetime(2024, 2, 9, 3, 47, tzinfo=datetime.timezone.utc)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_datetime_async_decorator(client):
    url = "/query/datetime/async_decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.datetime(2024, 2, 9, 3, 47, tzinfo=datetime.timezone.utc)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_datetime(client):
    url = "/query/datetime/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    v = datetime.datetime(2024, 2, 8, 22, 50, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_datetime_default(client):
    url = "/query/datetime/default"
    # Test that missing input for required and optional yields default values
    n_opt = datetime.datetime(2024, 2, 8, 21, 48)
    opt = datetime.datetime(2024, 2, 8, 21, 49)
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    # Test that present ISO 8601 input for required and optional yields input values
    opt = datetime.datetime(2024, 2, 9, 4, 7, tzinfo=datetime.timezone.utc)
    n_opt = datetime.datetime(2024, 2, 9, 4, 8, tzinfo=datetime.timezone.utc)
    r = client.get(url, query_string={"opt": opt.isoformat(), "n_opt": n_opt.isoformat()})
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_datetime_func(client):
    url = "/query/datetime/func"
    # Test that input passing func yields input
    v = datetime.datetime(2024, 2, 8, 23, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.datetime(2024, 4, 8, 23, 17)
    r = client.get(url, query_string={"v": v.strftime("%m/%d/%Y %I:%M %p")})
    assert "error" in r.json


def test_datetime_format(client):
    url = "/query/datetime/datetime_format"
    # Test that input passing format yields input
    v = datetime.datetime(2024, 2, 8, 23, 19)
    r = client.get(url, query_string={"v": v.strftime("%m/%d/%Y %I:%M %p")})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing format yields error
    v = datetime.datetime(2024, 2, 8, 23, 18, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "error" in r.json


# date Validation
def test_required_date(client):
    url = "/query/date/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.date(2024, 2, 9)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_date_decorator(client):
    url = "/query/date/decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.date(2024, 2, 9)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_date_async_decorator(client):
    url = "/query/date/async_decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.date(2024, 2, 9)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_date(client):
    url = "/query/date/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    v = datetime.date(2024, 2, 10)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_date_default(client):
    url = "/query/date/default"
    # Test that missing input for required and optional yields default values
    n_opt = datetime.date(2024, 2, 9)
    opt = datetime.date(2024, 2, 10)
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    # Test that present ISO 8601 input for required and optional yields input values
    opt = datetime.date(2024, 2, 9)
    n_opt = datetime.date(2024, 2, 10)
    r = client.get(url, query_string={"opt": opt.isoformat(), "n_opt": n_opt.isoformat()})
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_date_func(client):
    url = "/query/date/func"
    # Test that input passing func yields input
    v = datetime.date(2024, 2, 2)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.date(2024, 9, 9)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "error" in r.json


# time Validation
def test_required_time(client):
    url = "/query/time/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.time(23, 24, 21)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_time_decorator(client):
    url = "/query/time/decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.time(23, 24, 21)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_time_async_decorator(client):
    url = "/query/time/async_decorator/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.time(23, 24, 21)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_time(client):
    url = "/query/time/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    v = datetime.time(23, 24, 55)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that present non-ISO 8601 input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_time_default(client):
    url = "/query/time/default"
    # Test that missing input for required and optional yields default values
    n_opt = datetime.time(23, 21, 23)
    opt = datetime.time(23, 21, 35)
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    # Test that present ISO 8601 input for required and optional yields input values
    opt = datetime.time(23, 25, 42)
    n_opt = datetime.time(23, 26, 1)
    r = client.get(url, query_string={"opt": opt.isoformat(), "n_opt": n_opt.isoformat()})
    assert "opt" in r.json
    assert r.json["opt"] == opt.isoformat()
    assert "n_opt" in r.json
    assert r.json["n_opt"] == n_opt.isoformat()
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_time_func(client):
    url = "/query/time/func"
    # Test that input passing func yields input
    v = datetime.time(8)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.time(23, 26, 16)
    r = client.get(url, query_string={"v": v.isoformat()})
    assert "error" in r.json


# Union Validation
def test_required_union(client):
    url = "/query/union/required"
    # Test that present bool input yields input value
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 5541})
    assert "v" in r.json
    assert r.json["v"] == 5541
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool/int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_union_decorator(client):
    url = "/query/union/decorator/required"
    # Test that present bool input yields input value
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 5541})
    assert "v" in r.json
    assert r.json["v"] == 5541
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool/int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_union_async_decorator(client):
    url = "/query/union/async_decorator/required"
    # Test that present bool input yields input value
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 5541})
    assert "v" in r.json
    assert r.json["v"] == 5541
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-bool/int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_union(client):
    url = "/query/union/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present bool input yields input value
    r = client.get(url, query_string={"v": False})
    assert "v" in r.json
    assert r.json["v"] is False
    # Test that present int input yields input value
    r = client.get(url, query_string={"v": 8616})
    assert "v" in r.json
    assert r.json["v"] == 8616
    # Test that present non-bool/int input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_union_default(client):
    url = "/query/union/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] is True
    assert "opt" in r.json
    assert r.json["opt"] == 5
    # Test that present bool/int input for required and optional yields input values
    r = client.get(url, query_string={"opt": False, "n_opt": 6})
    assert "opt" in r.json
    assert r.json["opt"] is False
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 6
    # Test that present non-bool/int input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_union_func(client):
    url = "/query/union/func"
    # Test that bool input passing func yields input
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that int input passing func yields input
    r = client.get(url, query_string={"v": 7})
    assert "v" in r.json
    assert r.json["v"] == 7
    # Test that bool input failing func yields error
    r = client.get(url, query_string={"v": False})
    assert "error" in r.json
    # Test that int input failing func yields error
    r = client.get(url, query_string={"v": 0})
    assert "error" in r.json


# List Validation
def test_required_list_str(client, app):
    url = "/query/list/req_str"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single str input yields [input value]
    r = client.get(url, query_string={"v": "w"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "w"
    # Test that present CSV str input yields [input values]
    v = ["x", "y"]
    r = client.get(url, query_string={"v": ','.join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present list with 2 CSV empty strings yields two empty strings
    r = client.get(url, query_string={"v": ","})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    # Test that present str input in multiple of the same query param yields [input values]
    v = ["z", "a"]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present empty str input in multiple of the same query param yields [input values]
    v = ["", ""]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_required_list_str_decorator(client):
    url = "/query/list/decorator/req_str"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single str input yields [input value]
    r = client.get(url, query_string={"v": "w"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "w"
    # Test that present CSV str input yields [input values]
    v = ["x", "y"]
    r = client.get(url, query_string={"v": ','.join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present list with 2 CSV empty strings yields two empty strings
    r = client.get(url, query_string={"v": ","})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    # Test that present str input in multiple of the same query param yields [input values]
    v = ["z", "a"]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present empty str input in multiple of the same query param yields [input values]
    v = ["", ""]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_required_list_str_async_decorator(client):
    url = "/query/list/async_decorator/req_str"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single str input yields [input value]
    r = client.get(url, query_string={"v": "w"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "w"
    # Test that present CSV str input yields [input values]
    v = ["x", "y"]
    r = client.get(url, query_string={"v": ','.join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present list with 2 CSV empty strings yields two empty strings
    r = client.get(url, query_string={"v": ","})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    # Test that present str input in multiple of the same query param yields [input values]
    v = ["z", "a"]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present empty str input in multiple of the same query param yields [input values]
    v = ["", ""]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_required_list_str_disable_query_csv_unset(client, app):
    url = "/query/list/disable_query_csv/unset"
    # Test that FPV_LIST_DISABLE_QUERY_CSV returns array of two strings when False
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": False})
    v = ["b", "c"]
    r = client.get(f"{url}", query_string={"v": ",".join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that FPV_LIST_DISABLE_QUERY_CSV returns array of single string when True
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": True})
    v = "d,e"
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    list_assertion_helper(1, str, [v], r.json["v"])
    # Test that FPV_LIST_DISABLE_QUERY_CSV runs as False by default
    app.config.pop("FPV_LIST_DISABLE_QUERY_CSV", None)
    v = ["f", "g"]
    r = client.get(f"{url}", query_string={"v": ",".join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])


def test_required_list_str_disable_query_csv_true(client, app):
    url = "/query/list/disable_query_csv/true"
    # Test that FPV_LIST_DISABLE_QUERY_CSV of False can be overridden to True per-route
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": False})
    v = "h,i"
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    list_assertion_helper(1, str, [v], r.json["v"])
    # Test that FPV_LIST_DISABLE_QUERY_CSV of True can be 'overridden' to True per-route
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": True})
    v = "j,k"
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    list_assertion_helper(1, str, [v], r.json["v"])
    # Test that unset FPV_LIST_DISABLE_QUERY_CSV can be overridden to True per-route
    app.config.pop("FPV_LIST_DISABLE_QUERY_CSV", None)
    v = "l,m"
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    list_assertion_helper(1, str, [v], r.json["v"])


def test_required_list_str_disable_query_csv_false(client, app):
    url = "/query/list/disable_query_csv/false"
    # Test that FPV_LIST_DISABLE_QUERY_CSV of False can be 'overridden' to False per-route
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": False})
    v = ["n", "o"]
    r = client.get(f"{url}", query_string={"v": ",".join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that FPV_LIST_DISABLE_QUERY_CSV of True can be overridden to False per-route
    app.config.update({"FPV_LIST_DISABLE_QUERY_CSV": True})
    v = ["p", "q"]
    r = client.get(f"{url}", query_string={"v": ",".join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that unset FPV_LIST_DISABLE_QUERY_CSV can be 'overridden' to False per-route
    app.config.pop("FPV_LIST_DISABLE_QUERY_CSV", None)
    v = ["r", "s"]
    r = client.get(f"{url}", query_string={"v": ",".join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])


def test_optional_list_str(client):
    url = "/query/list/opt_str"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single str input yields [input value]
    r = client.get(url, query_string={"v": "t"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "t"
    # Test that present CSV str input yields [input values]
    v = ["u", "v"]
    r = client.get(url, query_string={"v": ','.join(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present list with 2 CSV empty strings yields two empty strings
    r = client.get(url, query_string={"v": ","})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    # Test that present str input in multiple of the same query param yields [input values]
    v = ["w", "x"]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present empty str input in multiple of the same query param yields [input values]
    v = ["", ""]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])


def test_required_list_int(client):
    url = "/query/list/req_int"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single int input yields [input value]
    r = client.get(url, query_string={"v": -1})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == -1
    # Test that present CSV int input yields [input values]
    v = [0, 1]
    r = client.get(url, query_string={"v": ','.join([str(i) for i in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present int input in multiple of the same param yields [input values]
    v = [2, 3]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present non-int list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_int(client):
    url = "/query/list/opt_int"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single int input yields [input value]
    r = client.get(url, query_string={"v": -1})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == -1
    # Test that present CSV int input yields [input values]
    v = [0, 1]
    r = client.get(url, query_string={"v": ','.join([str(i) for i in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present int input in multiple of the same param yields [input values]
    v = [2, 3]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present non-int list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json

def test_required_list_bool(client):
    url = "/query/list/req_bool"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single bool input yields [input value]
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is bool
    assert r.json["v"][0] is True
    # Test that present CSV bool input yields [input values]
    v = [False, True]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, bool, v, r.json["v"])
    # Test that present bool input in multiple of the same param yields [input values]
    v = [True, False]
    r = client.get(url, query_string={"v": ','.join([str(b) for b in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, bool, v, r.json["v"])
    # Test that present non-bool list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_bool(client):
    url = "/query/list/opt_bool"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single bool input yields [input value]
    r = client.get(url, query_string={"v": True})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is bool
    assert r.json["v"][0] is True
    # Test that present CSV bool input yields [input values]
    v = [False, True]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, bool, v, r.json["v"])
    # Test that present bool input in multiple of the same param yields [input values]
    v = [True, False]
    r = client.get(url, query_string={"v": ','.join([str(b) for b in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, bool, v, r.json["v"])
    # Test that present non-bool list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_float(client):
    url = "/query/list/req_float"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single float input yields [input value]
    r = client.get(url, query_string={"v": 7.39})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is float
    assert r.json["v"][0] == 7.39
    # Test that present CSV int input yields [input values]
    v = [1.2, 3.4]
    r = client.get(url, query_string={"v": ','.join([str(i) for i in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, float, v, r.json["v"])
    # Test that present int input in multiple of the same param yields [input values]
    v = [5.6, 7.8]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, float, v, r.json["v"])
    # Test that present non-int list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_float(client):
    url = "/query/list/opt_float"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single float input yields [input value]
    r = client.get(url, query_string={"v": 7.39})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is float
    assert r.json["v"][0] == 7.39
    # Test that present CSV int input yields [input values]
    v = [1.2, 3.4]
    r = client.get(url, query_string={"v": ','.join([str(i) for i in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, float, v, r.json["v"])
    # Test that present int input in multiple of the same param yields [input values]
    v = [5.6, 7.8]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, float, v, r.json["v"])
    # Test that present non-int list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_union(client):
    url = "/query/list/req_union"
    # Test that present single int input yields [input value]
    r = client.get(f"{url}?v=2")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == 2
    # Test that present single float input yields [input value]
    r = client.get(f"{url}?v=3.14")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is float
    assert r.json["v"][0] == 3.14
    # Test that present CSV int/float input yields [input values]
    r = client.get(f"{url}?v=4,5.62")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    assert type(r.json["v"][0]) is int
    assert type(r.json["v"][1]) is float
    assert r.json["v"][0] == 4
    assert r.json["v"][1] == 5.62
    # Test that present non-int/float list items yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

def test_required_list_union_everything(client):
    url = "/query/list/req_union_everything"
    # Test that list input yields input
    v = [
        "testing",
        5,
        True,
        3.14,
        datetime.datetime(2025, 4, 20, 15, 13, 32).isoformat(),
        datetime.date(2025, 4, 20).isoformat(),
        datetime.time(15, 14, 22).isoformat(),
        json.dumps({"i": "am", "a": "dictionary"}),
        Fruits.APPLE.value,
        Binary.ONE.value,
        str(uuid.uuid4())
    ]
    r = client.get(f"{url}", query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(v) == len(r.json["v"])
    for i in range(len(v)):
        if i == 7:
            assert r.json["v"][i] == json.loads(v[i])
        else:
            assert r.json["v"][i] == v[i]
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

def test_optional_list_union(client):
    url = "/query/list/opt_union"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single int input yields [input value]
    r = client.get(f"{url}?v=2")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == 2
    # Test that present single bool input yields [input value]
    r = client.get(f"{url}?v=true")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is bool
    assert r.json["v"][0] == True
    # Test that present CSV int/bool input yields [input values]
    r = client.get(f"{url}?v=4,false")
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    assert type(r.json["v"][0]) is int
    assert type(r.json["v"][1]) is bool
    assert r.json["v"][0] == 4
    assert r.json["v"][1] == False
    # Test that present non-int/bool list items yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json

def test_required_list_datetime(client):
    url = "/query/list/req_datetime"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single datetime input yields [input value]
    v0 = datetime.datetime(2024, 2, 10, 14, 31, 47)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV datetime input yields [input values]
    v = [datetime.datetime(2024, 2, 10, 14, 32, 38),
         datetime.datetime(2024, 2, 10, 14, 32, 53)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present datetime input in multiple of the same query param yields [input values]
    v = [datetime.datetime(2025, 4, 18, 16, 58, 19),
         datetime.datetime(2025, 4, 18, 16, 58, 39)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-datetime list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_datetime(client):
    url = "/query/list/opt_datetime"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single datetime input yields [input value]
    v0 = datetime.datetime(2024, 2, 10, 14, 31, 47)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV datetime input yields [input values]
    v = [datetime.datetime(2024, 2, 10, 14, 32, 38),
         datetime.datetime(2024, 2, 10, 14, 32, 53)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present datetime input in multiple of the same query param yields [input values]
    v = [datetime.datetime(2025, 4, 18, 16, 58, 19),
         datetime.datetime(2025, 4, 18, 16, 58, 39)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-datetime list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_date(client):
    url = "/query/list/req_date"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single date input yields [input value]
    v0 = datetime.date(2024, 2, 9)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV date input yields [input values]
    v = [datetime.date(2024, 2, 10), datetime.date(2024, 2, 11)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present date input in multiple of the same query param yields [input values]
    v = [datetime.date(2025, 2, 18), datetime.date(2025, 2, 19)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-date list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_date(client):
    url = "/query/list/opt_date"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single date input yields [input value]
    v0 = datetime.date(2024, 2, 9)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV date input yields [input values]
    v = [datetime.date(2024, 2, 10), datetime.date(2024, 2, 11)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present date input in multiple of the same query param yields [input values]
    v = [datetime.date(2025, 2, 18), datetime.date(2025, 2, 19)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-date list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_time(client):
    url = "/query/list/req_time"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single time input yields [input value]
    v0 = datetime.time(14, 37, 2)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV time input yields [input values]
    v = [datetime.time(14, 37, 34), datetime.time(14, 37, 45)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present time input in multiple of the same query param yields [input values]
    v = [datetime.time(17, 2, 45), datetime.time(17, 2, 55)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-time list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_time(client):
    url = "/query/list/opt_time"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single time input yields [input value]
    v0 = datetime.time(14, 37, 2)
    r = client.get(url, query_string={"v": v0.isoformat()})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v0.isoformat()
    # Test that present CSV time input yields [input values]
    v = [datetime.time(14, 37, 34), datetime.time(14, 37, 45)]
    r = client.get(url, query_string={"v": ','.join([d.isoformat() for d in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present time input in multiple of the same query param yields [input values]
    v = [datetime.time(17, 2, 45), datetime.time(17, 2, 55)]
    r = client.get(url, query_string={"v": [d.isoformat() for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"], expected_call="isoformat")
    # Test that present non-time list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


# list[dict] is not supported for Query unless query_list_disable_csv is set
def test_required_list_dict(client):
    url = "/query/list/req_dict"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single dict input yields [input value]
    v = {"hello": "world"}
    r = client.get(url, query_string={"v": json.dumps(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is dict
    assert r.json["v"][0] == v
    # Test that present dict input in multiple of the same query param yields [input values]
    v = [{"one": "dict"}, {"two": "dict", "red": "dict"}, {"blue": "dict"}]
    r = client.get(url, query_string={"v": [json.dumps(d) for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 3
    list_assertion_helper(2, dict, v, r.json["v"])
    # Test that present non-dict list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_dict(client):
    url = "/query/list/opt_dict"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single dict input yields [input value]
    v = {"hello": "world"}
    r = client.get(url, query_string={"v": json.dumps(v)})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is dict
    assert r.json["v"][0] == v
    # Test that present dict input in multiple of the same query param yields [input values]
    v = [{"one": "dict"}, {"two": "dict", "red": "dict"}, {"blue": "dict"}]
    r = client.get(url, query_string={"v": [json.dumps(d) for d in v]})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 3
    list_assertion_helper(3, dict, v, r.json["v"])
    # Test that present non-dict list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_str_enum(client):
    url = "/query/list/req_str_enum"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single Fruits input yields [input value]
    v = Fruits.APPLE
    r = client.get(url, query_string={"v": v.value})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v.value
    # Test that present CSV Fruits input yields [input values]
    v = [Fruits.APPLE.value, Fruits.ORANGE.value]
    r = client.get(url, query_string={"v": ','.join([e for e in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present Fruits input in multiple of the same query param yields [input values]
    v = [Fruits.APPLE.value, Fruits.ORANGE.value]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present non-Fruits list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_str_enum(client):
    url = "/query/list/opt_str_enum"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single Fruits input yields [input value]
    v = Fruits.APPLE
    r = client.get(url, query_string={"v": v.value})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v.value
    # Test that present CSV Fruits input yields [input values]
    v = [Fruits.ORANGE.value, Fruits.APPLE.value]
    r = client.get(url, query_string={"v": ','.join([e for e in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present Fruits input in multiple of the same query param yields [input values]
    v = [Fruits.APPLE.value, Fruits.ORANGE.value]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present non-Fruits list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_list_int_enum(client):
    url = "/query/list/req_int_enum"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single Binary input yields [input value]
    v = Binary.ZERO
    r = client.get(url, query_string={"v": v.value})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == v.value
    # Test that present CSV Binary input yields [input values]
    v = [Binary.ONE.value, Binary.ONE.value]
    r = client.get(url, query_string={"v": ','.join([str(e) for e in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present Binary input in multiple of the same query param yields [input values]
    v = [
        Binary.ONE.value, Binary.ZERO.value, Binary.ZERO.value,
        Binary.ONE.value, Binary.ONE.value
    ]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 5
    list_assertion_helper(5, int, v, r.json["v"])
    # Test that present non-Binary list items yields error
    r = client.get(url, query_string={"v": "crying zeros and I'm hearing"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_int_enum(client):
    url = "/query/list/opt_int_enum"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single Binary input yields [input value]
    v = Binary.ONE
    r = client.get(url, query_string={"v": v.value})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is int
    assert r.json["v"][0] == v.value
    # Test that present CSV Binary input yields [input values]
    v = [Binary.ONE.value]*2
    r = client.get(url, query_string={"v": ','.join([str(e) for e in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present Binary input in multiple of the same query param yields [input values]
    v = [Binary.ONE.value]*2
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, int, v, r.json["v"])
    # Test that present non-Binary list items yields error
    r = client.get(url, query_string={"v": "Cut my somersaults, sign my backflip"})
    assert "error" in r.json


def test_required_list_uuid(client):
    url = "/query/list/req_uuid"
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single UUID input yields [input value]
    v = str(uuid.uuid4())
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v
    # Test that present CSV UUID input yields [input values]
    v = [str(uuid.uuid4()), str(uuid.uuid4())]
    r = client.get(url, query_string={"v": ','.join([u for u in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present UUID input in multiple of the same query param yields [input values]
    v = [str(uuid.uuid4()), str(uuid.uuid4())]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present non-UUID list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_optional_list_uuid(client):
    url = "/query/list/opt_uuid"
    # Test the missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present single empty string input yields empty list
    r = client.get(url, query_string={"v": ""})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 0
    # Test that present single UUID input yields [input value]
    v = str(uuid.uuid4())
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == v
    # Test that present CSV UUID input yields [input values]
    v = [str(uuid.uuid4()), str(uuid.uuid4())]
    r = client.get(url, query_string={"v": ','.join([u for u in v])})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present UUID input in multiple of the same query param yields [input values]
    v = [str(uuid.uuid4()), str(uuid.uuid4())]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that present non-UUID list items yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_list_default(client):
    url = "/query/list/default"
    # Test that missing input for required and optional yields default values
    n_opt = ["a", "b"]
    opt = [0, 1]
    r = client.get(url)
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])
    # Test that present bool input for required and optional yields [input values]
    opt = [2, 3]
    n_opt = ["c", "d"]
    r = client.get(url, query_string={"opt": opt, "n_opt": n_opt})
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])


def test_list_default_decorator(client):
    url = "/query/list/decorator/default"
    # Test that missing input for required and optional yields default values
    n_opt = ["a", "b"]
    opt = [0, 1]
    r = client.get(url)
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])
    # Test that present bool input for required and optional yields [input values]
    opt = [2, 3]
    n_opt = ["c", "d"]
    r = client.get(url, query_string={"opt": opt, "n_opt": n_opt})
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])


def test_list_default_async_decorator(client):
    url = "/query/list/async_decorator/default"
    # Test that missing input for required and optional yields default values
    n_opt = ["a", "b"]
    opt = [0, 1]
    r = client.get(url)
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])
    # Test that present bool input for required and optional yields [input values]
    opt = [2, 3]
    n_opt = ["c", "d"]
    r = client.get(url, query_string={"opt": opt, "n_opt": n_opt})
    assert "n_opt" in r.json
    assert type(r.json["n_opt"]) is list
    assert len(r.json["n_opt"]) == 2
    list_assertion_helper(2, str, n_opt, r.json["n_opt"])
    assert "opt" in r.json
    assert type(r.json["opt"]) is list
    assert len(r.json["opt"]) == 2
    list_assertion_helper(2, int, opt, r.json["opt"])


def test_list_func(client):
    url = "/query/list/func"
    # Test that input passing func yields input
    v = [0.1, 0.2]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, float, v, r.json["v"])
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": [0.3, 0.4, 0.5]})
    assert "error" in r.json


def test_min_list_length(client):
    url = "/query/list/min_list_length"
    # Test that below length yields error
    r = client.get(url, query_string={"v": ["short", "list"]})
    assert "error" in r.json
    # Test that at length yields [input values]
    v = ["kinda", "longer", "list"]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 3
    list_assertion_helper(3, str, v, r.json["v"])
    # Test that above length yields [input values]
    v = ["the", "longest", "of", "lists"]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 4
    list_assertion_helper(4, str, v, r.json["v"])


def test_max_list_length(client):
    url = "/query/list/max_list_length"
    # Test that below length yields [input values]
    v = ["short", "list"]
    r = client.get(url, query_string={"v": v})
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that at length yields [input values]
    v = ["kinda", "longer", "list"]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 3
    list_assertion_helper(3, str, v, r.json["v"])
    # Test that above length yields error
    r = client.get(url, query_string={"v": ["the", "longest", "of", "lists"]})
    assert "error" in r.json


def test_non_typing_list_str(client):
    url = "/query/list/non_typing"
    # Test that present single str input yields [input value]
    r = client.get(url, query_string={"v": "w"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "w"
    # Test that present CSV str input yields [input values]
    v = ["x", "y"]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json


def test_non_typing_optional_list_str(client):
    url = "/query/list/optional_non_typing"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
        # Test that present str input yields [input value]
    r = client.get(url, query_string={"v": "test"})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 1
    assert type(r.json["v"][0]) is str
    assert r.json["v"][0] == "test"
    # Test that present CSV str input yields [input values]
    v = ["two", "tests"]
    r = client.get(url, query_string={"v": v})
    assert "v" in r.json
    assert type(r.json["v"]) is list
    assert len(r.json["v"]) == 2
    list_assertion_helper(2, str, v, r.json["v"])


# Enum validation
def test_required_str_enum(client):
    url = "/query/str_enum/required"
    # Test that present str_enum input yields input value
    r = client.get(url, query_string={"v": Fruits.APPLE.value})
    assert "v" in r.json
    assert r.json["v"] == Fruits.APPLE.value
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-str_enum input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_str_enum(client):
    url = "/query/str_enum/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present str_enum input yields input value
    r = client.get(url, query_string={"v": Fruits.ORANGE.value})
    assert "v" in r.json
    assert r.json["v"] == Fruits.ORANGE.value
    # Test that present non-str_enum input yields error
    r = client.get(url, query_string={"v": "v"})
    assert "error" in r.json


def test_str_enum_default(client):
    url = "/query/str_enum/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == Fruits.APPLE.value
    assert "opt" in r.json
    assert r.json["opt"] == Fruits.ORANGE.value
    # Test that present str_enum input for required and optional yields input values
    r = client.get(url, query_string={"opt": Fruits.ORANGE.value, "n_opt": Fruits.APPLE.value})
    assert "opt" in r.json
    assert r.json["opt"] == Fruits.ORANGE.value
    assert "n_opt" in r.json
    assert r.json["n_opt"] == Fruits.APPLE.value
    # Test that present non-str_enum input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_str_enum_func(client):
    url = "/query/str_enum/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": Fruits.ORANGE.value})
    assert "v" in r.json
    assert r.json["v"] == Fruits.ORANGE.value
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": Fruits.APPLE.value})
    assert "error" in r.json


def test_required_int_enum(client):
    url = "/query/int_enum/required"
    # Test that present int_enum input yields input value
    r = client.get(url, query_string={"v": Binary.ONE.value})
    assert "v" in r.json
    assert r.json["v"] == Binary.ONE.value
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-int_enum input yields error
    r = client.get(url, query_string={"v": 8})
    assert "error" in r.json


def test_optional_int_enum(client):
    url = "/query/int_enum/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present int_enum input yields input value
    r = client.get(url, query_string={"v": Binary.ZERO.value})
    assert "v" in r.json
    assert r.json["v"] == Binary.ZERO.value
    # Test that present non-int_enum input yields error
    r = client.get(url, query_string={"v": 8})
    assert "error" in r.json


def test_int_enum_default(client):
    url = "/query/int_enum/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == Binary.ZERO.value
    assert "opt" in r.json
    assert r.json["opt"] == Binary.ONE.value
    # Test that present int_enum input for required and optional yields input values
    r = client.get(url, query_string={"opt": Binary.ONE.value, "n_opt": Binary.ZERO.value})
    assert "opt" in r.json
    assert r.json["opt"] == Binary.ONE.value
    assert "n_opt" in r.json
    assert r.json["n_opt"] == Binary.ZERO.value
    # Test that present non-int_enum input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": 9})
    assert "error" in r.json


def test_int_enum_func(client):
    url = "/query/int_enum/func"
    # Test that input passing func yields input
    r = client.get(url, query_string={"v": Binary.ZERO.value})
    assert "v" in r.json
    assert r.json["v"] == Binary.ZERO.value
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": Binary.ONE.value})
    assert "error" in r.json

# UUID Validation
def test_required_uuid(client):
    url = "/query/uuid/required"
    # Test that present UUID input yields input value
    u = uuid.uuid4()
    r = client.get(url, query_string={"v": u})
    assert "v" in r.json
    assert uuid.UUID(r.json["v"]) == u
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-UUID input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_uuid_decorator(client):
    url = "/query/uuid/decorator/required"
    # Test that present UUID input yields input value
    u = uuid.uuid4()
    r = client.get(url, query_string={"v": u})
    assert "v" in r.json
    assert uuid.UUID(r.json["v"]) == u
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-UUID input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_required_uuid_async_decorator(client):
    url = "/query/uuid/async_decorator/required"
    # Test that present UUID input yields input value
    u = uuid.uuid4()
    r = client.get(url, query_string={"v": u})
    assert "v" in r.json
    assert uuid.UUID(r.json["v"]) == u
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json
    # Test that present non-UUID input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json


def test_optional_uuid(client):
    url = "/query/uuid/optional"
    # Test that missing input yields None
    r = client.get(url)
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present UUID input yields input value
    u = uuid.uuid4()
    r = client.get(url, query_string={"v": u})
    assert "v" in r.json
    assert uuid.UUID(r.json["v"]) == u
    # Test that present non-UUID input yields error
    r = client.get(url, query_string={"v": "a"})
    assert "error" in r.json

def test_uuid_default(client):
    url = "/query/uuid/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "9ba0c75f-1574-4464-bd7d-760262e3ea41"
    assert "opt" in r.json
    assert r.json["opt"] == "2f01faa3-29a2-4b36-b406-2ad288fb4969"
    # Test that present UUID input for required and optional yields input values
    r = client.get(url, query_string={
        "opt": "f2b1e5a0-e050-4618-83b8-f303b887b75d",
        "n_opt": "48c0d213-a889-4ba6-9722-70f6e6a1afca"
    })
    assert "opt" in r.json
    assert r.json["opt"] == "f2b1e5a0-e050-4618-83b8-f303b887b75d"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "48c0d213-a889-4ba6-9722-70f6e6a1afca"
    # Test that present non-UUID input for required yields error
    r = client.get(url, query_string={"opt": "a", "n_opt": "b"})
    assert "error" in r.json


def test_uuid_func(client):
    url = "/query/uuid/func"
    # Test that input passing func yields input
    u = "b662e5f5-7e82-4ac7-8844-4efea3afa171"
    r = client.get(url, query_string={"v": u})
    assert "v" in r.json
    assert r.json["v"] == u
    # Test that input failing func yields error
    r = client.get(url, query_string={"v": "492c6dfc-1730-11f0-9cd2-0242ac120002"})
    assert "error" in r.json


def test_dict_args_str_str(client):
    url = "/query/dict/args/str/str"
    # Test that correct input yields input value
    d = {"hi": "ho"}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    d = {"hi": -45}
    # Test that incorrect input yields error
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json


def test_dict_args_str_union(client):
    url = "/query/dict/args/str/union"
    # Test that union input yields input value
    d = {"hi": "ho", "id": 1}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that only one type also yields input value
    d = {"hi": 90, "id": 1}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that empty dict yields input value
    d = {}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d


def test_dict_args_str_list(client):
    url = "/query/dict/args/str/list"
    # Test that correct input yields input value
    d = {"1.3": False, "9.0": [2, 4, 5]}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that empty dict yields input value
    d = {}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that incorrect values yields error
    d = {"test": False, "ing": [2, True, 5]}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_list_dict_args_str_union(client):
    url = "/query/list/dict/args/str/union"
    # Test that correct input yields input value
    d = [{"id": 3, "chicken": "noodle soup"}, {}, {"foo": "bar"}]
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that empty list yields input value
    d = []
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that incorrect values yields error
    d = [{"id": 1.03, "name": "foo"}, {"id": -1}]
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json


if sys.version_info >= (3, 10):
    def test_union_requred_3_10(client):
        url = "/query/union/3_10/required"
        # Test that missing input yields error
        r = client.get(url)
        assert "error" in r.json
        # Test that present datetime input yields input value
        d = datetime.datetime.now()
        r = client.get(url, query_string={"v": d})
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()
        # Test that present bool input yields input value
        d = True
        r = client.get(url, query_string={"v": d})
        assert "v" in r.json
        assert r.json["v"] == d
        d = {"v": "string"}
        # Test that present non-bool/datetime input yields error
        r = client.get(url, query_string={"v": d})
        assert "error" in r.json

    def test_union_optional_3_10(client):
        url = "/query/union/3_10/optional"
        # Test that missing input yields input value
        r = client.get(url)
        assert "v" in r.json
        assert r.json["v"] is None
        # Test that present datetime input yields input value
        d = datetime.datetime.now()
        r = client.get(url, query_string={"v": d})
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()
        # Test that present bool input yields input value
        d = True
        r = client.get(url, query_string={"v": d})
        assert "v" in r.json
        assert r.json["v"] == d
        d = "string"
        # Test that present non-bool/datetime input yields error
        r = client.get(url, query_string={"v": d})
        assert "error" in r.json

    def test_dict_args_str_3_10_union(client):
        url = "/query/dict/args/str/3_10_union"
        # Test that union input yields input value
        d = {"hi": "ho", "id": 1}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that only one type also yields input value
        d = {"hi": 90, "id": 1}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that empty dict yields input value
        d = {}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d

    def test_dict_args_str_list_3_10_union(client):
        url = "/query/dict/args/str/list/3_10_union"
        # Test that correct input yields input value
        d = {"1.3": False, "9.0": [2, 4, 5]}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that empty dict yields input value
        d = {}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that incorrect values yields error
        d = {"test": False, "ing": [2, True, 5]}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "error" in r.json

def test_typeddict_normal(client):
    url = "/query/typeddict/"
    # Test that correct input yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing keys yields error
    d = {"id": 3}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json
    # Test that incorrect values yields error
    d = {"id": 1.03, "name": "foo", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_functional(client):
    url = "/query/typeddict/functional"
    # Test that correct input yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing keys yields error
    d = {"id": 3}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json
    # Test that incorrect values yields error
    d = {"id": 1.03, "name": "foo", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_optional(client):
    url = "/query/typeddict/optional"
    # Test that correct input yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that no input yields input value
    d = None
    r = client.get(url, query_string={"v": d})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing keys yields error
    d = {"id": 3}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json
    # Test that empty dict yields error
    d = {}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

if sys.version_info >= (3, 10):
    def test_typeddict_union_optional(client):
        url = "/query/typeddict/union_optional"
        # Test that correct input yields input value
        d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that no input yields input value
        d = None
        r = client.get(url, query_string={"v": d})
        assert "v" in r.json
        assert r.json["v"] == d
        # Test that missing keys yields error
        d = {"id": 3}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "error" in r.json
        # Test that empty dict yields error
        d = {}
        r = client.get(url, query_string={"v": json.dumps(d)})
        assert "error" in r.json

def test_typeddict_default(client):
    url = "/query/typeddict/default"
    # Test that missing input for required and optional yields default values
    r = client.get(url)
    assert "n_opt" in r.json
    assert r.json["n_opt"] == {"id": 1, "name": "Bob", "timestamp": datetime.datetime(2025, 11, 18, 0, 0).isoformat()}
    assert "opt" in r.json
    assert r.json["opt"] == {"id": 2, "name": "Billy", "timestamp": datetime.datetime(2025, 11, 18, 5, 30).isoformat()}
    # Test that present TypedDict input for required and optional yields input values
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={
        "opt": json.dumps(d),
        "n_opt": json.dumps(d),
    })
    assert "opt" in r.json
    assert r.json["opt"] == d
    assert "n_opt" in r.json
    assert r.json["n_opt"] == d
    # Test that present non-TypedDict input for required yields error
    r = client.get(url, query_string={"opt": {"id": 3}, "n_opt": "b"})
    assert "error" in r.json

def test_typeddict_func(client):
    url = "/query/typeddict/func"
    # Test that correct input yields input value
    d = {"id": 3, "name": "Bill", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that func failing input yields input value
    d = {"id": 3, "name": "Billy Bob Joe", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_json_schema(client):
    url = "/query/typeddict/json_schema"
    # Test that correct input yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing keys yields error
    d = {"id": 3}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json
    # Test that incorrect values yields error
    d = {"id": 1.03, "name": "foo", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_not_required(client):
    url = "/query/typeddict/not_required"
    # Test that all keys yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing not requried key yields input value
    d = {"name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing required keys yields error
    d = {"name": "Merriweather"}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_required(client):
    url = "/query/typeddict/required"
    # Test that all keys yields input value
    d = {"id": 3, "name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing not requried key yields input value
    d = {"name": "Merriweather", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that missing required keys yields error
    d = {"name": "Merriweather"}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

def test_typeddict_complex(client):
    url = "/query/typeddict/complex"
    # Test that correct input yields input value
    d = {
        "name": "change da world",
        "children": [
            {
                "id": 4,
                "name": "my final message. Goodb ye",
                "timestamp": datetime.datetime.now().isoformat(),
            }
        ],
        "left": {
            "x": 3.4,
            "y": 1.0,
            "z": 99999.34455663
        },
        "right": {
            "x": 3.2,
            "y": 1.1,
            "z": 999.3663
        },
    }
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that empty children list yields input value
    d = {
        "name": "change da world",
        "children": [],
        "left": {
            "x": 3.4,
            "y": 1.0,
            "z": 99999.34455663
        },
        "right": {
            "x": 3.2,
            "y": 1.1,
            "z": 999.3663
        },
    }
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that incorrect child TypedDict yields error
    d = {
        "name": "change da world",
        "children": [
            {
                "id": 4,
                "name": 6,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        ],
        "left": {
            "x": 3.4,
            "y": 1.0,
            "z": 99999.34455663
        },
        "right": {
            "x": 3.2,
            "y": 1.1,
            "z": 999.3663
        },
    }
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json
    # Test that omitting NotRequired key in child yields input value
    d = {
        "name": "tags",
        "children": [
            {
                "id": 4,
                "name": "ice my wrist",
                "timestamp": datetime.datetime.now().isoformat(),
            }
        ],
        "left": {
            "x": 3.4,
            "y": 1.0,
            "z": 99999.34455663
        },
        "right": {
            "x": 3.2,
            "y": 1.1,
            "z": 999.3663
        },
    }
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "v" in r.json
    assert r.json["v"] == d
    # Test that incorrect values yields error
    d = {"id": 1.03, "name": "foo", "timestamp": datetime.datetime.now().isoformat()}
    r = client.get(url, query_string={"v": json.dumps(d)})
    assert "error" in r.json

