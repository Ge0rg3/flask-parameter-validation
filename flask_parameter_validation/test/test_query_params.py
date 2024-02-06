def test_required_str(client):
    r = client.get("/query/required_str?value=value")
    assert "value" in r.json
    assert r.json["value"] == "value"
    r = client.get("/query/required_str")
    assert "error" in r.json

def test_optional_str(client):
    r = client.get("/query/optional_str")
    assert "value" in r.json
    assert r.json["value"] is None
    r = client.get("/query/optional_str?value=value")
    assert "value" in r.json
    assert r.json["value"] == "value"

def test_str_default(client):
    r = client.get("/query/str_default")
    assert "optional" in r.json
    assert r.json["optional"] == "optional"
    assert "not_optional" in r.json
    assert r.json["not_optional"] == "not_optional"
    r = client.get("/query/str_default?optional=a&not_optional=b")
    assert "optional" in r.json
    assert r.json["optional"] == "a"
    assert "not_optional" in r.json
    assert r.json["not_optional"] == "b"

def test_str_min_str_length(client):
    r = client.get("/query/str_min_str_length?v=")
    assert "error" in r.json
    r = client.get("/query/str_min_str_length?v=a")
    assert "v" in r.json
    assert r.json["v"] == "a"
    r = client.get("/query/str_min_str_length?v=aa")
    assert "v" in r.json
    assert r.json["v"] == "aa"