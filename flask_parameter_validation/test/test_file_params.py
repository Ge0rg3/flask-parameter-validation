import datetime
import filecmp
from pathlib import Path
from typing import Type, List, Optional

resources = Path(__file__).parent / 'resources'


def test_required_file(client):
    url = "/file/required"
    # Test that we receive a success response if a file is provided
    r = client.post(url, data={"v": (resources / "test.json").open("rb")})
    assert "success" in r.json
    assert r.json["success"]
    # Test that we receive an error if a file is not provided
    r = client.post(url)
    assert "error" in r.json


def test_optional_file(client):
    url = "/file/optional"
    # Test that we receive a success response if a file is provided
    r = client.post(url, data={"v": (resources / "test.json").open("rb")})
    assert "success" in r.json
    assert r.json["success"]
    assert "file_provided" in r.json
    assert r.json["file_provided"] is True
    # Test that we receive an error if a file is not provided
    r = client.post(url)
    assert "success" in r.json
    assert r.json["success"]
    assert "file_provided" in r.json
    assert r.json["file_provided"] is False


def test_file_content_types(client):
    url = "/file/content_types"
    # Test that we receive a success response if a file of correct Content-Type is provided
    r = client.post(url, data={"v": (resources / "test.json").open("rb")})
    assert "success" in r.json
    assert r.json["success"]
    # Test that we receive an error if a file of incorrect Content-Type is provided
    r = client.post(url, data={"v": (resources / "hubble_mars_10kB.jpg").open("rb")})
    assert "error" in r.json


def test_file_min_length(client):
    url = "/file/min_length"
    # Test that we receive a success response if a file of correct Content-Length is provided
    load_path = resources / "hubble_mars_10kB.jpg"
    r = client.post(url, data={"v": load_path.open("rb")})
    assert "success" in r.json
    assert r.json["success"]
    assert "save_path" in r.json
    assert filecmp.cmp(load_path, r.json["save_path"])
    # Test that we receive an error if a file of incorrect Content-Length is provided
    r = client.post(url, data={"v": (resources / "test.json").open("rb")})
    assert "error" in r.json

def test_file_max_length(client):
    url = "/file/max_length"
    # Test that we receive a success response if a file of correct Content-Length is provided
    load_path = resources / "hubble_mars_10kB.jpg"
    r = client.post(url, data={"v": load_path.open("rb")})
    assert "success" in r.json
    assert r.json["success"]
    assert "save_path" in r.json
    assert filecmp.cmp(load_path, r.json["save_path"])
    # Test that we receive an error if a file of incorrect Content-Length is provided
    r = client.post(url, data={"v": (resources / "aldrin_47kB.jpg").open("rb")})
    assert "error" in r.json
