# String Validation
import datetime
from typing import Type, List, Optional

from flask_parameter_validation.test.enums import Fruits, Binary


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
    url = "/route/str/required"
    # Test that present input yields input value
    r = client.get(f"{url}/v")
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404


def test_required_str_decorator(client):
    url = "/route/str/decorator/required"
    # Test that present input yields input value
    r = client.get(f"{url}/v")
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404


def test_required_str_async_decorator(client):
    url = "/route/str/async_decorator/required"
    # Test that present input yields input value
    r = client.get(f"{url}/v")
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404


def test_str_min_str_length(client):
    url = "/route/str/min_str_length"
    # Test that below minimum yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(f"{url}/aa")
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above minimum yields input
    r = client.get(f"{url}/aaa")
    assert "v" in r.json
    assert r.json["v"] == "aaa"


def test_str_max_str_length(client):
    url = "/route/str/max_str_length"
    # Test that below maximum yields input
    r = client.get(f"{url}/a")
    assert "v" in r.json
    assert r.json["v"] == "a"
    # Test that at maximum yields input
    r = client.get(f"{url}/aa")
    assert "v" in r.json
    assert r.json["v"] == "aa"
    # Test that above maximum yields error
    r = client.get(f"{url}/aaa")
    assert "error" in r.json


def test_str_whitelist(client):
    url = "/route/str/whitelist"
    # Test that input within whitelist yields input
    r = client.get(f"{url}/ABC123")
    assert "v" in r.json
    assert r.json["v"] == "ABC123"
    # Test that mixed input yields error
    r = client.get(f"{url}/abc123")
    assert "error" in r.json
    # Test that input outside of whitelist yields error
    r = client.get(f"{url}/def456")
    assert "error" in r.json


def test_str_blacklist(client):
    url = "/route/str/blacklist"
    # Test that input within blacklist yields error
    r = client.get(f"{url}/ABC123")
    assert "error" in r.json
    # Test that mixed input yields error
    r = client.get(f"{url}/abc123")
    assert "error" in r.json
    # Test that input outside of blacklist yields input
    r = client.get(f"{url}/def456")
    assert "v" in r.json
    assert r.json["v"] == "def456"


def test_str_pattern(client):
    url = "/route/str/pattern"
    # Test that input matching pattern yields input
    r = client.get(f"{url}/AbC123")
    assert "v" in r.json
    assert r.json["v"] == "AbC123"
    # Test that input failing pattern yields error
    r = client.get(f"{url}/123ABC")
    assert "error" in r.json


def test_str_func(client):
    url = "/route/str/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/123")
    assert "v" in r.json
    assert r.json["v"] == "123"
    # Test that input failing func yields error
    r = client.get(f"{url}/abc")
    assert "error" in r.json


def test_str_json_schema(client):
    url = "/route/str/json_schema"
    # Test that input matching schema yields input
    r = client.get(f"{url}/test@example.com")
    assert "v" in r.json
    assert r.json["v"] == "test@example.com"
    # Test that input failing schema yields error
    r = client.get(f"{url}/notanemail")
    assert "error" in r.json


# Int Validation
def test_required_int(client):
    url = "/route/int/required"
    # Test that present int input yields input value
    r = client.get(f"{url}/1")
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-int input is 404
    r = client.get(f"{url}/a")
    assert r.status_code == 404


def test_int_min_int(client):
    url = "/route/int/min_int"
    # Test that below minimum yields error
    r = client.get(f"{url}/-1")
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(f"{url}/0")
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above minimum yields input
    r = client.get(f"{url}/1")
    assert "v" in r.json
    assert r.json["v"] == 1


def test_int_max_int(client):
    url = "/route/int/max_int"
    # Test that below maximum yields input
    r = client.get(f"{url}/-1")
    assert "v" in r.json
    assert r.json["v"] == -1
    # Test that at maximum yields input
    r = client.get(f"{url}/0")
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above maximum yields error
    r = client.get(f"{url}/1")
    assert "error" in r.json


def test_int_func(client):
    url = "/route/int/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/8")
    assert "v" in r.json
    assert r.json["v"] == 8
    # Test that input failing func yields error
    r = client.get(f"{url}/9")
    assert "error" in r.json


def test_int_json_schema(client):
    url = "/route/int/json_schema"
    # Test that input matching schema yields input
    r = client.get(f"{url}/10")
    assert "v" in r.json
    assert r.json["v"] == 10
    # Test that input failing schema yields error
    r = client.get(f"{url}/100")
    assert "error" in r.json


# Bool Validation
def test_required_bool(client):
    url = "/route/bool/required"
    # Test that present bool input yields input value
    r = client.get(f"{url}/true")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-bool input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_bool_func(client):
    url = "/route/bool/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/true")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that input failing func yields error
    r = client.get(f"{url}/false")
    assert "error" in r.json


# Float Validation
def test_required_float(client):
    url = "/route/float/required"
    # Test that present float input yields input value
    r = client.get(f"{url}/1.2")
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present int input yields float(input) value
    r = client.get(f"{url}/1.0")
    assert "v" in r.json
    assert r.json["v"] == 1.0
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-float input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_float_func(client):
    url = "/route/float/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/3.141592")
    assert "v" in r.json
    assert r.json["v"] == 3.141592
    # Test that input failing func yields error
    r = client.get(f"{url}/3.15")
    assert "error" in r.json


def test_float_json_schema(client):
    url = "/route/float/json_schema"
    # Test that input matching schema yields input
    r = client.get(f"{url}/3.14")
    assert "v" in r.json
    assert r.json["v"] == 3.14
    # Test that input failing schema yields error
    r = client.get(f"{url}/3.141592")
    assert "error" in r.json


# datetime Validation
def test_required_datetime(client):
    url = "/route/datetime/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.datetime(2024, 2, 9, 3, 47, tzinfo=datetime.timezone.utc)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_datetime_func(client):
    url = "/route/datetime/func"
    # Test that input passing func yields input
    v = datetime.datetime(2024, 2, 8, 23, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.datetime(2024, 4, 8, 23, 17)
    r = client.get(f"{url}/{v.isoformat}")
    assert "error" in r.json


def test_datetime_format(client):
    url = "/route/datetime/datetime_format"
    # Test that input passing format yields input
    v = datetime.datetime(2024, 2, 8, 23, 19)
    r = client.get(f"{url}/{v.strftime('%m/%d/%Y %I:%M %p')}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing format yields error
    v = datetime.datetime(2024, 2, 8, 23, 18, tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    r = client.get(f"{url}/{v.isoformat()}")
    assert "error" in r.json


# date Validation
def test_required_date(client):
    url = "/route/date/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.date(2024, 2, 9)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_date_func(client):
    url = "/route/date/func"
    # Test that input passing func yields input
    v = datetime.date(2024, 2, 2)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.date(2024, 9, 9)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "error" in r.json


# time Validation
def test_required_time(client):
    url = "/route/time/required"
    # Test that present ISO 8601 input yields input value
    v = datetime.time(23, 24, 21)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_time_func(client):
    url = "/route/time/func"
    # Test that input passing func yields input
    v = datetime.time(8)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "v" in r.json
    assert r.json["v"] == v.isoformat()
    # Test that input failing func yields error
    v = datetime.time(23, 26, 16)
    r = client.get(f"{url}/{v.isoformat()}")
    assert "error" in r.json


# Union Validation
def test_required_union(client):
    url = "/route/union/required"
    # Test that present bool input yields input value
    r = client.get(f"{url}/true")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present int input yields input value
    r = client.get(f"{url}/5541")
    assert "v" in r.json
    assert r.json["v"] == 5541
    # Test that missing input is 404
    r = client.get(f"{url}")
    assert r.status_code == 404
    # Test that present non-bool/int input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_union_func(client):
    url = "/route/union/func"
    # Test that bool input passing func yields input
    r = client.get(f"{url}/true")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that int input passing func yields input
    r = client.get(f"{url}/7")
    assert "v" in r.json
    assert r.json["v"] == 7
    # Test that bool input failing func yields error
    r = client.get(f"{url}/false")
    assert "error" in r.json
    # Test that int input failing func yields error
    r = client.get(f"{url}/0")
    assert "error" in r.json


# Enum validation
def test_required_str_enum(client):
    url = "/route/str_enum/required"
    # Test that present str_enum input yields input value
    r = client.get(f"{url}/{Fruits.APPLE.value}")
    assert "v" in r.json
    assert r.json["v"] == Fruits.APPLE.value
    # Test that missing input is 404
    r = client.get(url)
    assert r.status_code == 404
    # Test that present non-str_enum input yields error
    r = client.get(f"{url}/a")
    assert "error" in r.json


def test_str_enum_func(client):
    url = "/route/str_enum/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/{Fruits.ORANGE.value}")
    assert "v" in r.json
    assert r.json["v"] == Fruits.ORANGE.value
    # Test that input failing func yields error
    r = client.get(f"{url}/{Fruits.APPLE.value}")
    assert "error" in r.json


def test_required_int_enum(client):
    url = "/route/int_enum/required"
    # Test that present int_enum input yields input value
    r = client.get(f"{url}/{Binary.ONE.value}")
    assert "v" in r.json
    assert r.json["v"] == Binary.ONE.value
    # Test that missing input is 404
    r = client.get(url)
    assert r.status_code == 404
    # Test that present non-int_enum input yields error
    r = client.get(f"{url}/8")
    assert "error" in r.json


def test_int_enum_func(client):
    url = "/route/int_enum/func"
    # Test that input passing func yields input
    r = client.get(f"{url}/{Binary.ZERO.value}")
    assert "v" in r.json
    assert r.json["v"] == Binary.ZERO.value
    # Test that input failing func yields error
    r = client.get(f"{url}/{Binary.ONE.value}")
    assert "error" in r.json
