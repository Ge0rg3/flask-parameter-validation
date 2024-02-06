def test_str(client):
    r = client.get("/query/str?value=value")
    json = r.json
    assert "value" in json
    assert json["value"] == "value"
    r = client.get("/query/str")
    print(r.text)