from flask_parameter_validation.docs_blueprint import get_route_docs

def test_http_ok(client):
    r = client.get("/docs/")
    assert r.status_code == 200
    r = client.get("/docs/json")
    assert r.status_code == 200

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
    types = {
        "bool": {"opt": "Optional[bool, NoneType]", "n_opt": "bool"},
        "date": {"opt": "Optional[date, NoneType]", "n_opt": "date"},
        "datetime": {"opt": "Optional[datetime, NoneType]", "n_opt": "datetime"},
        "dict": {"opt": "Optional[dict, NoneType]", "n_opt": "dict"},
        "float": {"opt": "Optional[float, NoneType]", "n_opt": "float"},
        "int": {"opt": "Optional[int, NoneType]", "n_opt": "int"},
        "int_enum": {"opt": "Optional[Binary, NoneType]", "n_opt": "Binary"},
        "list": {"opt": "Optional[List[int], NoneType]", "n_opt": "List[str]"},
        "str": {"opt": "Optional[str, NoneType]", "n_opt": "str"},
        "str_enum": {"opt": "Optional[Fruits, NoneType]", "n_opt": "Fruits"},
        "time": {"opt": "Optional[time, NoneType]", "n_opt": "time"},
        "union": {"opt": "Union[bool, int, NoneType]", "n_opt": "Union[bool, int]"}
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
