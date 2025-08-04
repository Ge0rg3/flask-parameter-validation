import sys
from flask_parameter_validation.docs_blueprint import get_route_docs

def test_http_ok(client):
    r = client.get("/docs/")
    assert r.status_code == 200
    r = client.get("/docs/json")
    assert r.status_code == 200
import sys
def test_routes_added(app):
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    for doc in get_route_docs():
        assert doc["rule"] in routes

def test_doc_types_of_default(app):
    locs = {
        "form": "Form",
        "json": "Json",
        "query": "Query",
        "route": "Route"
    }
    optional_as_str = "Optional" if sys.version_info >= (3,10) else "Union"
    types = {
        "bool": {"opt": f"{optional_as_str}[bool, NoneType]", "n_opt": "bool"},
        "date": {"opt": f"{optional_as_str}[date, NoneType]", "n_opt": "date"},
        "datetime": {"opt": f"{optional_as_str}[datetime, NoneType]", "n_opt": "datetime"},
        "dict": {"opt": f"{optional_as_str}[dict, NoneType]", "n_opt": "dict"},
        "float": {"opt": f"{optional_as_str}[float, NoneType]", "n_opt": "float"},
        "int": {"opt": f"{optional_as_str}[int, NoneType]", "n_opt": "int"},
        "int_enum": {"opt": f"{optional_as_str}[Binary, NoneType]", "n_opt": "Binary"},
        "list": {"opt": f"{optional_as_str}[List[int], NoneType]", "n_opt": "List[str]"},
        "str": {"opt": f"{optional_as_str}[str, NoneType]", "n_opt": "str"},
        "str_enum": {"opt": f"{optional_as_str}[Fruits, NoneType]", "n_opt": "Fruits"},
        "time": {"opt": f"{optional_as_str}[time, NoneType]", "n_opt": "time"},
        "union": {"opt": "Union[bool, int, NoneType]", "n_opt": "Union[bool, int]"},
        "uuid": {"opt": f"{optional_as_str}[UUID, NoneType]", "n_opt": "UUID"}
    }
    route_unsupported_types = ["dict", "list"]
    route_docs = get_route_docs()
    for loc in locs.keys():
        for arg_type in types.keys():
            if loc == "route" and arg_type in route_unsupported_types:
                continue
            route_to_check = f"/{loc}/{arg_type}/default"
            for doc in route_docs:
                if doc["rule"] == route_to_check:
                    args = doc["args"][locs[loc]]
                    if args[0]["name"] == "n_opt":
                        n_opt = args[0]
                        opt = args[1]
                    else:
                        opt = args[0]
                        n_opt = args[1]
                    assert n_opt["type"] == types[arg_type]["n_opt"]
                    assert opt["type"] == types[arg_type]["opt"]
