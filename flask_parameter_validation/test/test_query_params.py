# String Validation
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
