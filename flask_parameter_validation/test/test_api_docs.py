import sys
from typing import Callable, Any
import pytest
from flask_parameter_validation.docs_blueprint import get_route_docs, generate_openapi_docs
from flask_parameter_validation.test.testing_blueprints.dict_blueprint import _fpv_test_dict_blueprint_json_schema


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
        "uuid": {"opt": f"{optional_as_str}[UUID, NoneType]", "n_opt": "UUID"},
        "typeddict": {"opt": f"{optional_as_str}[Simple, NoneType]", "n_opt": "Simple"},
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

@pytest.fixture(scope="session")
def openapi_docs(app):
    return generate_openapi_docs()

def check_schema_against_parameters(schema, openapi_parameters):
    all_keys = schema["properties"].keys()
    for key in all_keys:
        found_key = False
        for parameter in openapi_parameters:
            if parameter["name"] == key:
                found_key = True
                if "required" in schema and key in schema["required"]:
                    assert parameter["required"]
                else:
                    assert "required" not in parameter or not parameter["required"]
                for schema_key, schema_data in schema["properties"][key].items():
                    assert schema_key in parameter["schema"]
                    assert parameter["schema"][schema_key] == schema["properties"][key][schema_key]
        assert found_key

def check_schema_for_all_locations(openapi_docs, schema, type_and_test, skip_route: bool = False):
    check_schema_against_parameters(schema, openapi_docs["paths"][f"/query/{type_and_test}"]["get"]["parameters"])
    if not skip_route:
        check_schema_against_parameters(schema, openapi_docs["paths"][f"/route/{type_and_test}/{{v}}"]["get"]["parameters"])
    assert schema == openapi_docs["paths"][f"/form/{type_and_test}"]["post"]["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]
    assert schema == openapi_docs["paths"][f"/json/{type_and_test}"]["post"]["requestBody"]["content"]["application/json"]["schema"]


def test_openapi_docs_min_str_length(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "minLength": 2,
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/min_str_length")

def test_openapi_docs_max_str_length(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "maxLength": 2,
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/max_str_length")

def test_openapi_docs_optional(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "null"}
                ]
            }
        },
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/optional", skip_route=True)

def test_openapi_docs_pattern(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "pattern": "\\w{3}\\d{3}",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/pattern")

def test_openapi_docs_min_int(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "minimum": 0,
                "type": "integer"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "int/min_int")

def test_openapi_docs_max_int(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "maximum": 0,
                "type": "integer"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "int/max_int")

def test_openapi_docs_bool(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "type": "boolean"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "bool/required")

def test_openapi_docs_float(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "type": "number"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "float/required")

def test_openapi_docs_datetime(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "format": "date-time",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "datetime/required")

def test_openapi_docs_date(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "format": "date",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "date/required")

def test_openapi_docs_time(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "format": "time",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "time/required")

def test_openapi_docs_typeddict_required(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "timestamp": {"format": "date-time", "type": "string"},
                },
                "required": ["name", "timestamp"],
                "title": "SimpleRequired",
                "type": "object",
                "description": "Comment in the decorator"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "typeddict/required", skip_route=True)

def test_openapi_docs_typeddict_notrequired(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "description": "Docstring of SimpleNotRequired",
                "properties": {
                    "id": {"type": "integer", "description": "Annotated comment on the id property"},
                    "name": {"type": "string", "description": "# comment on the name property"},
                    "timestamp": {"format": "date-time", "type": "string"},
                },
                "required": ["name", "timestamp"],
                "title": "SimpleNotRequired",
                "type": "object"
            },
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "typeddict/not_required", skip_route=True)

def test_openapi_docs_typeddict_title(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "timestamp": {"format": "date-time", "type": "string"},
                },
                "required": ["id", "name", "timestamp"],
                "title": "Simple",
                "description": "Overrides the class docstring",  # The class docstring is "A simple TypedDict," but is overridden by a comment in the Parameter subclass constructor
                "type": "object"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "typeddict/", skip_route=True)

def test_openapi_docs_typeddict_property_comment_overrides_property_class_docstring(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "properties": {
                    "children": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "title": "Simple",
                            "description": "A simple TypedDict",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "timestamp": {"format": "date-time", "type": "string"},
                            },
                            "required": ["id", "name", "timestamp"],
                        }
                    },
                    "left": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "z": {"type": "number"}
                        },
                        "required": ["x", "y", "z"],
                        "title": "Coord",
                        "description": "Docstring of Coord"
                    },
                    "right": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "z": {"type": "number"}
                        },
                        "required": ["x", "y", "z"],
                        "title": "Coord",
                        "description": "Overrides the docstring of Coord"  # The class docstring is "Docstring of Coord," but is overridden by a comment on the right property of Complex
                    },
                    "name": {"type": "string"},
                },
                "required": ["children", "left", "right", "name"],
                "title": "Complex",
                "type": "object"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "typeddict/complex", skip_route=True)

def test_openapi_docs_str_enum(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "description": "Possible fruits",
                "oneOf": [
                    {
                        "const": "apple",
                        "description": "An apple a day keeps the doctor away, so they say",
                        "title": "APPLE"
                    },
                    {
                        "const": "orange",
                        "description": "Oranges contain vitamin C, which might also keep the doctor away",
                        "title": "ORANGE"
                    }
                ],
                "title": "Fruits",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str_enum/required")

def test_openapi_docs_int_enum(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "description": "Possible binary values",
                "oneOf": [
                    {
                        "const": 0,
                        "description": "Logic level low",
                        "title": "ZERO"
                    },
                    {
                        "const": 1,
                        "description": "Logic level high",
                        "title": "ONE"
                    }
                ],
                "title": "Binary",
                "type": "integer"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "int_enum/required")

def test_openapi_docs_uuid(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "format": "uuid",
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "uuid/required")

def test_openapi_docs_optional_list_union(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "oneOf": [
                    {
                        "items": {
                            "oneOf": [
                                {"type": "integer"},
                                {"type": "boolean"},
                            ]
                        },
                        "type": "array"
                    },
                    {
                        "type": "null"
                    }
                ],
            }
        },
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "list/opt_union", skip_route=True)

def test_openapi_docs_min_list_length(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "items": {"type": "string"},
                "minItems": 3,
                "type": "array"
            }
        },
        "type": "object",
        "required": ["v"]
    }
    check_schema_for_all_locations(openapi_docs, schema, "list/min_list_length", skip_route=True)

def test_openapi_docs_max_list_length(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "items": {"type": "string"},
                "maxItems": 3,
                "type": "array"
            }
        },
        "type": "object",
        "required": ["v"]
    }
    check_schema_for_all_locations(openapi_docs, schema, "list/max_list_length", skip_route=True)

def test_openapi_docs_dict(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "type": "object"
            }
        },
        "type": "object",
        "required": ["v"]
    }
    check_schema_for_all_locations(openapi_docs, schema, "dict/required", skip_route=True)

def test_openapi_docs_dict_json_schema(openapi_docs):
    schema = {
        "properties": {
            "v": _fpv_test_dict_blueprint_json_schema
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "dict/json_schema", skip_route=True)

if sys.version_info >= (3, 10):
    def test_openapi_docs_dict_args_3_10_union(openapi_docs):
        schema = {
            "properties": {
                "v": {
                    "additionalProperties": {
                        "oneOf": [
                            {
                                "type": "array",
                                "items": {
                                    "type": "integer"
                                }
                            },
                            {
                                "type": "boolean"
                            }
                        ]
                    },
                    "type": "object"
                }
            },
            "required": ["v"],
            "type": "object"
        }
        check_schema_for_all_locations(openapi_docs, schema, "dict/args/str/list/3_10_union", skip_route=True)

def test_openapi_docs_dict_args(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "additionalProperties": {
                    "oneOf": [
                        {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            }
                        },
                        {
                            "type": "boolean"
                        }
                    ]
                },
                "type": "object"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "dict/args/str/list", skip_route=True)


def test_openapi_docs_default(openapi_docs):
    schema = {
        "properties": {
            "n_opt": {
                "type": "string",
                "default": "not_optional"
            },
            "opt": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "null"}
                ],
                "default": "optional"
            }
        },
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/async_decorator/default", skip_route=True)


def test_openapi_docs_alias(openapi_docs):
    schema = {
        "properties": {
            "v": {
                "type": "string"
            }
        },
        "required": ["v"],
        "type": "object"
    }
    check_schema_for_all_locations(openapi_docs, schema, "str/decorator/alias", skip_route=True)

def test_openapi_docs_undeprecated_route(openapi_docs):
    type_and_test = "str/async_decorator/func"
    openapi_operations = [
        openapi_docs["paths"][f"/query/{type_and_test}"]["get"],
        openapi_docs["paths"][f"/route/{type_and_test}/{{v}}"]["get"],
        openapi_docs["paths"][f"/form/{type_and_test}"]["post"],
        openapi_docs["paths"][f"/json/{type_and_test}"]["post"]
    ]
    for operation in openapi_operations:
        assert "deprecated" not in operation

def test_openapi_docs_deprecated_route(openapi_docs):
    type_and_test = "str/async_decorator/deprecated"
    openapi_operations = [
        openapi_docs["paths"][f"/query/{type_and_test}"]["get"],
        openapi_docs["paths"][f"/route/{type_and_test}/{{v}}"]["get"],
        openapi_docs["paths"][f"/form/{type_and_test}"]["post"],
        openapi_docs["paths"][f"/json/{type_and_test}"]["post"]
    ]
    for operation in openapi_operations:
        assert "deprecated" in operation and operation["deprecated"]

def test_openapi_docs_file(openapi_docs):
    assert "application/octet-stream" in openapi_docs["paths"]["/file/required"]["post"]["requestBody"]["content"]

def test_openapi_docs_content_type(openapi_docs):
    assert "application/json" in openapi_docs["paths"]["/file/content_types"]["post"]["requestBody"]["content"]