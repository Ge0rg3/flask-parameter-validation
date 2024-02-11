# String Validation
import datetime
from typing import Type, List, Optional


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
