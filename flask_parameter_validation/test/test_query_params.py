# String Validation
import datetime


def test_required_str(client):
    url = "/query/str/required"
    # Test that present input yields input value
    r = client.get(f"{url}?v=v")
    assert "v" in r.json
    assert r.json["v"] == "v"
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json


def test_optional_str(client):
    url = "/query/str/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present input yields input value
    r = client.get(f"{url}?v=v")
    assert "v" in r.json
    assert r.json["v"] == "v"


def test_str_default(client):
    url = "/query/str/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "opt" in r.json
    assert r.json["opt"] == "optional"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "not_optional"
    # Test that present input for required and optional yields input values
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "opt" in r.json
    assert r.json["opt"] == "a"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "b"


def test_str_min_str_length(client):
    url = "/query/str/min_str_length"
    # Test that below minimum yields error
    r = client.get(f"{url}?v=")
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(f"{url}?v=a")
    assert "v" in r.json
    assert r.json["v"] == "a"
    # Test that above minimum yields input
    r = client.get(f"{url}?v=aa")
    assert "v" in r.json
    assert r.json["v"] == "aa"


def test_str_max_str_length(client):
    url = "/query/str/max_str_length"
    # Test that below maximum yields input
    r = client.get(f"{url}?v=")
    assert "v" in r.json
    assert r.json["v"] == ""
    # Test that at maximum yields input
    r = client.get(f"{url}?v=a")
    assert "v" in r.json
    assert r.json["v"] == "a"
    # Test that above maximum yields error
    r = client.get(f"{url}?v=aa")
    assert "error" in r.json


def test_str_whitelist(client):
    url = "/query/str/whitelist"
    # Test that input within whitelist yields input
    r = client.get(f"{url}?v=ABC123")
    assert "v" in r.json
    assert r.json["v"] == "ABC123"
    # Test that mixed input yields error
    r = client.get(f"{url}?v=abc123")
    assert "error" in r.json
    # Test that input outside of whitelist yields error
    r = client.get(f"{url}?v=def456")
    assert "error" in r.json


def test_str_blacklist(client):
    url = "/query/str/blacklist"
    # Test that input within blacklist yields error
    r = client.get(f"{url}?v=ABC123")
    assert "error" in r.json
    # Test that mixed input yields error
    r = client.get(f"{url}?v=abc123")
    assert "error" in r.json
    # Test that input outside of blacklist yields input
    r = client.get(f"{url}?v=def456")
    assert "v" in r.json
    assert r.json["v"] == "def456"


def test_str_pattern(client):
    url = "/query/str/pattern"
    # Test that input matching pattern yields input
    r = client.get(f"{url}?v=AbC123")
    assert "v" in r.json
    assert r.json["v"] == "AbC123"
    # Test that input failing pattern yields error
    r = client.get(f"{url}?v=123ABC")
    assert "error" in r.json


def test_str_func(client):
    url = "/query/str/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=123")
    assert "v" in r.json
    assert r.json["v"] == "123"
    # Test that input failing func yields error
    r = client.get(f"{url}?v=abc")
    assert "error" in r.json


def test_str_alias(client):
    url = "/query/str/alias"
    # Test that original name yields error
    r = client.get(f"{url}?value=abc")
    assert "error" in r.json
    # Test that alias yields input
    r = client.get(f"{url}?v=abc")
    assert "value" in r.json
    assert r.json["value"] == "abc"


# Int Validation
def test_required_int(client):
    url = "/query/int/required"
    # Test that present int input yields input value
    r = client.get(f"{url}?v=1")
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-int input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_int(client):
    url = "/query/int/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present int input yields input value
    r = client.get(f"{url}?v=1")
    assert "v" in r.json
    assert r.json["v"] == 1
    # Test that present non-int input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_int_default(client):
    url = "/query/int/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 1
    assert "opt" in r.json
    assert r.json["opt"] == 2
    # Test that present int input for required and optional yields input values
    r = client.get(f"{url}?opt=3&n_opt=4")
    assert "opt" in r.json
    assert r.json["opt"] == 3
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 4
    # Test that present non-int input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_int_min_int(client):
    url = "/query/int/min_int"
    # Test that below minimum yields error
    r = client.get(f"{url}?v=-1")
    assert "error" in r.json
    # Test that at minimum yields input
    r = client.get(f"{url}?v=0")
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above minimum yields input
    r = client.get(f"{url}?v=1")
    assert "v" in r.json
    assert r.json["v"] == 1


def test_int_max_int(client):
    url = "/query/int/max_int"
    # Test that below maximum yields input
    r = client.get(f"{url}?v=-1")
    assert "v" in r.json
    assert r.json["v"] == -1
    # Test that at maximum yields input
    r = client.get(f"{url}?v=0")
    assert "v" in r.json
    assert r.json["v"] == 0
    # Test that above maximum yields error
    r = client.get(f"{url}?v=1")
    assert "error" in r.json


def test_int_func(client):
    url = "/query/int/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=8")
    assert "v" in r.json
    assert r.json["v"] == 8
    # Test that input failing func yields error
    r = client.get(f"{url}?v=9")
    assert "error" in r.json


# Bool Validation
def test_required_bool(client):
    url = "/query/bool/required"
    # Test that present lowercase bool input yields input value
    r = client.get(f"{url}?v=true")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present mixed-case bool input yields input value
    r = client.get(f"{url}?v=TruE")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present uppercase bool input yields input value
    r = client.get(f"{url}?v=TRUE")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-bool input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_bool(client):
    url = "/query/bool/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present bool input yields input value
    r = client.get(f"{url}?v=True")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that present non-bool input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_bool_default(client):
    url = "/query/bool/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] is False
    assert "opt" in r.json
    assert r.json["opt"] is True
    # Test that present bool input for required and optional yields input values
    r = client.get(f"{url}?opt=False&n_opt=True")
    assert "opt" in r.json
    assert r.json["opt"] is False
    assert "n_opt" in r.json
    assert r.json["n_opt"] is True
    # Test that present non-bool input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_bool_func(client):
    url = "/query/bool/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=True")
    assert "v" in r.json
    assert r.json["v"] is True
    # Test that input failing func yields error
    r = client.get(f"{url}?v=False")
    assert "error" in r.json


# Float Validation
def test_required_float(client):
    url = "/query/float/required"
    # Test that present float input yields input value
    r = client.get(f"{url}?v=1.2")
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present int input yields float(input) value
    r = client.get(f"{url}?v=1")
    assert "v" in r.json
    assert r.json["v"] == 1.0
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-float input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_float(client):
    url = "/query/float/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present float input yields input value
    r = client.get(f"{url}?v=1.2")
    assert "v" in r.json
    assert r.json["v"] == 1.2
    # Test that present non-float input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_float_default(client):
    url = "/query/float/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 2.3
    assert "opt" in r.json
    assert r.json["opt"] == 3.4
    # Test that present float input for required and optional yields input values
    r = client.get(f"{url}?opt=4.5&n_opt=5.6")
    assert "opt" in r.json
    assert r.json["opt"] == 4.5
    assert "n_opt" in r.json
    assert r.json["n_opt"] == 5.6
    # Test that present non-float input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_float_func(client):
    url = "/query/float/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=3.141592")
    assert "v" in r.json
    assert r.json["v"] == 3.141592
    # Test that input failing func yields error
    r = client.get(f"{url}?v=3.15")
    assert "error" in r.json

# datetime Validation
def test_required_datetime(client):
    url = "/query/datetime/required"
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=2024-02-09T03:47Z")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-09T03:47:00+00:00"
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_datetime(client):
    url = "/query/datetime/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=2024-02-08T22:50-05:00")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-08T22:50:00-05:00"
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_datetime_default(client):
    url = "/query/datetime/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "2024-02-08T21:48:00"
    assert "opt" in r.json
    assert r.json["opt"] == "2024-02-08T21:49:00"
    # Test that present ISO 8601 input for required and optional yields input values
    r = client.get(f"{url}?opt=2024-02-09T04:07Z&n_opt=2024-02-09T04:08Z")
    assert "opt" in r.json
    assert r.json["opt"] == "2024-02-09T04:07:00+00:00"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "2024-02-09T04:08:00+00:00"
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_datetime_func(client):
    url = "/query/datetime/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=2024-02-08T23:15-05:00")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-08T23:15:00-05:00"
    # Test that input failing func yields error
    r = client.get(f"{url}?v=4/8/2024 11:17 PM")
    assert "error" in r.json


def test_datetime_format(client):
    url = "/query/datetime/datetime_format"
    # Test that input passing format yields input
    r = client.get(f"{url}?v=2/8/2024 11:19 PM")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-08T23:19:00"
    # Test that input failing format yields error
    r = client.get(f"{url}?v=2024-02-08T23:18-05:00")
    assert "error" in r.json

# date Validation
def test_required_date(client):
    url = "/query/date/required"
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=2024-02-09")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-09"
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_date(client):
    url = "/query/date/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=2024-02-10")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-10"
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_date_default(client):
    url = "/query/date/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "2024-02-09"
    assert "opt" in r.json
    assert r.json["opt"] == "2024-02-10"
    # Test that present ISO 8601 input for required and optional yields input values
    r = client.get(f"{url}?opt=2024-02-09&n_opt=2024-02-10")
    assert "opt" in r.json
    assert r.json["opt"] == "2024-02-09"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "2024-02-10"
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_date_func(client):
    url = "/query/date/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=2024-02-02")
    assert "v" in r.json
    assert r.json["v"] == "2024-02-02"
    # Test that input failing func yields error
    r = client.get(f"{url}?v=2024-09-09")
    assert "error" in r.json

# time Validation
def test_required_time(client):
    url = "/query/time/required"
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=23:24:21")
    assert "v" in r.json
    assert r.json["v"] == "23:24:21"
    # Test that missing input yields error
    r = client.get(f"{url}")
    assert "error" in r.json
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=a")
    assert "error" in r.json


def test_optional_time(client):
    url = "/query/time/optional"
    # Test that missing input yields None
    r = client.get(f"{url}")
    assert "v" in r.json
    assert r.json["v"] is None
    # Test that present ISO 8601 input yields input value
    r = client.get(f"{url}?v=23:24:55")
    assert "v" in r.json
    assert r.json["v"] == "23:24:55"
    # Test that present non-ISO 8601 input yields error
    r = client.get(f"{url}?v=v")
    assert "error" in r.json


def test_time_default(client):
    url = "/query/time/default"
    # Test that missing input for required and optional yields default values
    r = client.get(f"{url}")
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "23:21:23"
    assert "opt" in r.json
    assert r.json["opt"] == "23:21:35"
    # Test that present ISO 8601 input for required and optional yields input values
    r = client.get(f"{url}?opt=23:25:42&n_opt=23:26:01")
    assert "opt" in r.json
    assert r.json["opt"] == "23:25:42"
    assert "n_opt" in r.json
    assert r.json["n_opt"] == "23:26:01"
    # Test that present non-ISO 8601 input for required yields error
    r = client.get(f"{url}?opt=a&n_opt=b")
    assert "error" in r.json


def test_time_func(client):
    url = "/query/time/func"
    # Test that input passing func yields input
    r = client.get(f"{url}?v=08:00:00")
    assert "v" in r.json
    assert r.json["v"] == "08:00:00"
    # Test that input failing func yields error
    r = client.get(f"{url}?v=23:27:16")
    assert "error" in r.json
