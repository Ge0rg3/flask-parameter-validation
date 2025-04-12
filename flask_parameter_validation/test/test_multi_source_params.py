import datetime
import json

import pytest

from flask_parameter_validation.test.testing_application import multi_source_sources

common_parameters = "source_a, source_b", [(source_a['name'], source_b['name']) for source_a in multi_source_sources for source_b in multi_source_sources]

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_bool(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_bool"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        b = True
        if source == "query":
            r = client.get(url, query_string={"v": b})
        elif source == "form":
            r = client.get(url, data={"v": b})
        elif source == "json":
            r = client.get(url, json={"v": b})
        elif source == "route":
            r = client.get(f"{url}/{b}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] is True

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_bool(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_bool"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        b = True
        if source == "query":
            r = client.get(url, query_string={"v": b})
        elif source == "form":
            r = client.get(url, data={"v": b})
        elif source == "json":
            r = client.get(url, json={"v": b})
        elif source == "route":
            r = client.get(f"{url}/{b}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] is True
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_date(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    d = datetime.date(2024, 6, 1)
    url = f"/ms_{source_a}_{source_b}/required_date"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": d.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": d.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": d.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{d.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_date(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    d = datetime.date(2024, 6, 1)
    url = f"/ms_{source_a}_{source_b}/optional_date"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": d.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": d.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": d.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{d.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_datetime(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    d = datetime.datetime(2024, 6, 1, 15, 44)
    url = f"/ms_{source_a}_{source_b}/required_datetime"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": d.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": d.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": d.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{d.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_datetime(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    d = datetime.datetime(2024, 6, 1, 15, 45)
    url = f"/ms_{source_a}_{source_b}/optional_datetime"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": d.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": d.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": d.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{d.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == d.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_dict(client, source_a, source_b):
    if source_a == source_b or "route" in [source_a, source_b]:  # Duplicate sources shouldn't be something someone does, so we won't test for it, Route does not support parameters of type 'dict'
        return
    d = {"a": "b"}
    url = f"/ms_{source_a}_{source_b}/required_dict"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": json.dumps(d)})
        elif source == "form":
            r = client.get(url, data={"v": json.dumps(d)})
        elif source == "json":
            r = client.get(url, json={"v": d})
        assert r is not None
        assert "v" in r.json
        assert json.dumps(r.json["v"]) == json.dumps(d)

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_dict(client, source_a, source_b):
    if source_a == source_b or "route" in [source_a, source_b]:  # Duplicate sources shouldn't be something someone does, so we won't test for it, Route does not support parameters of type 'dict'
        return
    d = {"c": "d"}
    url = f"/ms_{source_a}_{source_b}/optional_dict"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": json.dumps(d)})
        elif source == "form":
            r = client.get(url, data={"v": json.dumps(d)})
        elif source == "json":
            r = client.get(url, json={"v": d})
        assert r is not None
        assert "v" in r.json
        assert json.dumps(r.json["v"]) == json.dumps(d)
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_float(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_float"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        f = 3.14
        if source == "query":
            r = client.get(url, query_string={"v": f})
        elif source == "form":
            r = client.get(url, data={"v": f})
        elif source == "json":
            r = client.get(url, json={"v": f})
        elif source == "route":
            r = client.get(f"{url}/{f}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == f

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_float(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_float"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        f = 3.14
        if source == "query":
            r = client.get(url, query_string={"v": f})
        elif source == "form":
            r = client.get(url, data={"v": f})
        elif source == "json":
            r = client.get(url, json={"v": f})
        elif source == "route":
            r = client.get(f"{url}/{f}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == f
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_int(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_int"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        i = 3
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == i

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_int(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_int"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        i = 3
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == i
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_list(client, source_a, source_b):
    if source_a == source_b or "route" in [source_a, source_b]:  # Duplicate sources shouldn't be something someone does, so we won't test for it, Route does not support parameters of type 'List'
        return
    l = [1, 2]
    url = f"/ms_{source_a}_{source_b}/required_list"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": l})
        elif source == "form":
            r = client.get(url, data={"v": l})
        elif source == "json":
            r = client.get(url, json={"v": l})
        assert r is not None
        assert "v" in r.json
        assert json.dumps(r.json["v"]) == json.dumps(l)

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_list(client, source_a, source_b):
    if source_a == source_b or "route" in [source_a, source_b]:  # Duplicate sources shouldn't be something someone does, so we won't test for it, Route does not support parameters of type 'List'
        return
    l = [1, 2]
    url = f"/ms_{source_a}_{source_b}/optional_list"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": l})
        elif source == "form":
            r = client.get(url, data={"v": l})
        elif source == "json":
            r = client.get(url, json={"v": l})
        assert r is not None
        assert "v" in r.json
        assert json.dumps(r.json["v"]) == json.dumps(l)
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None


@pytest.mark.parametrize(*common_parameters)
def test_multi_source_str(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_str"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        s = "Testing MultiSource"
        if source == "query":
            r = client.get(url, query_string={"v": s})
        elif source == "form":
            r = client.get(url, data={"v": s})
        elif source == "json":
            r = client.get(url, json={"v": s})
        elif source == "route":
            r = client.get(f"{url}/{s}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == s

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_str(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_str"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        s = "Testing MultiSource"
        if source == "query":
            r = client.get(url, query_string={"v": s})
        elif source == "form":
            r = client.get(url, data={"v": s})
        elif source == "json":
            r = client.get(url, json={"v": s})
        elif source == "route":
            r = client.get(f"{url}/{s}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == s
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None


@pytest.mark.parametrize(*common_parameters)
def test_multi_source_time(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    t = datetime.time(16, 43)
    url = f"/ms_{source_a}_{source_b}/required_time"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": t.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": t.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": t.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{t.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == t.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_datetime(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    t = datetime.time(16, 44)
    url = f"/ms_{source_a}_{source_b}/optional_time"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        if source == "query":
            r = client.get(url, query_string={"v": t.isoformat()})
        elif source == "form":
            r = client.get(url, data={"v": t.isoformat()})
        elif source == "json":
            r = client.get(url, json={"v": t.isoformat()})
        elif source == "route":
            r = client.get(f"{url}/{t.isoformat()}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == t.isoformat()
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None


@pytest.mark.parametrize(*common_parameters)
def test_multi_source_union(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_union"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        i = 1
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == i
        s = "Testing MultiSource Union"
        if source == "query":
            r = client.get(url, query_string={"v": s})
        elif source == "form":
            r = client.get(url, data={"v": s})
        elif source == "json":
            r = client.get(url, json={"v": s})
        elif source == "route":
            r = client.get(f"{url}/{s}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == s

    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_union(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_union"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        i = 1
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == i
        s = "Testing MultiSource Union"
        if source == "query":
            r = client.get(url, query_string={"v": s})
        elif source == "form":
            r = client.get(url, data={"v": s})
        elif source == "json":
            r = client.get(url, json={"v": s})
        elif source == "route":
            r = client.get(f"{url}/{s}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == s
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None


@pytest.mark.parametrize(*common_parameters)
def test_multi_source_kwargs(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/kwargs"
    for source in [source_a, source_b]:
        # Test that present input matching validation yields input value
        r = None
        i = 3
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == i
        # Test that present input failing validation yields error
        r = None
        i = -1
        if source == "query":
            r = client.get(url, query_string={"v": i})
        elif source == "form":
            r = client.get(url, data={"v": i})
        elif source == "json":
            r = client.get(url, json={"v": i})
        elif source == "route":
            r = client.get(f"{url}/{i}")
        assert r is not None
        assert "error" in r.json
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_uuid(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/required_uuid"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        b = "926aaf11-57f1-4ba6-90ba-91333de13e6d"
        if source == "query":
            r = client.get(url, query_string={"v": b})
        elif source == "form":
            r = client.get(url, data={"v": b})
        elif source == "json":
            r = client.get(url, json={"v": b})
        elif source == "route":
            r = client.get(f"{url}/{b}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == b
    # Test that missing input yields error
    r = client.get(url)
    assert "error" in r.json

@pytest.mark.parametrize(*common_parameters)
def test_multi_source_optional_uuid(client, source_a, source_b):
    if source_a == source_b:  # This shouldn't be something someone does, so we won't test for it
        return
    url = f"/ms_{source_a}_{source_b}/optional_uuid"
    for source in [source_a, source_b]:
        # Test that present input yields input value
        r = None
        b = "28124cee-c074-448d-be63-6490ff5c89c0"
        if source == "query":
            r = client.get(url, query_string={"v": b})
        elif source == "form":
            r = client.get(url, data={"v": b})
        elif source == "json":
            r = client.get(url, json={"v": b})
        elif source == "route":
            r = client.get(f"{url}/{b}")
        assert r is not None
        assert "v" in r.json
        assert r.json["v"] == "28124cee-c074-448d-be63-6490ff5c89c0"
    # Test that missing input yields error
    r = client.get(url)
    assert r.json["v"] is None