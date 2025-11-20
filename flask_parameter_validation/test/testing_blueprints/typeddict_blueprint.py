import datetime
import sys
from typing import Optional

if sys.version_info >= (3, 11):
    from typing import NotRequired, Required, is_typeddict, TypedDict
elif sys.version_info >= (3, 9):
    from typing_extensions import NotRequired, Required, is_typeddict, TypedDict

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_typeddict_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    typeddict_bp = Blueprint(bp_name, __name__, url_prefix="/typeddict")
    decorator = getattr(typeddict_bp, http_verb)

    # TypedDict not currently supported by Route
    # def path(base: str, route_additions: str) -> str:
    #     return base + (route_additions if ParamType is Route else "")

    class Simple(TypedDict):
        id: int
        name: str
        timestamp: datetime.datetime

    @decorator("/")
    @ValidateParameters()
    def normal(v: Simple = ParamType(list_disable_query_csv=True)):
        assert type(v) is dict
        assert "id" in v and "name" in v and "timestamp" in v
        assert type(v["id"]) is int
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    SimpleFunc = TypedDict("SimpleFunc", {"id": int, "name": str, "timestamp": datetime.datetime})

    @decorator("/functional")
    @ValidateParameters()
    def functional(v: SimpleFunc = ParamType(list_disable_query_csv=True)):
        assert type(v) is dict
        assert "id" in v and "name" in v and "timestamp" in v
        assert type(v["id"]) is int
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})
    
    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[Simple] = ParamType(list_disable_query_csv=True)):
        if v is not None:
            assert type(v) is dict
            assert "id" in v and "name" in v and "timestamp" in v
            assert type(v["id"]) is int
            assert type(v["name"]) is str
            assert type(v["timestamp"]) is datetime.datetime
            v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    if sys.version_info >= (3, 10):
        @decorator("/union_optional")
        @ValidateParameters()
        def union_optional(v: Simple | None = ParamType(list_disable_query_csv=True)):
            if v is not None:
                assert type(v) is dict
                assert "id" in v and "name" in v and "timestamp" in v
                assert type(v["id"]) is int
                assert type(v["name"]) is str
                assert type(v["timestamp"]) is datetime.datetime
                v["timestamp"] = v["timestamp"].isoformat()
            return jsonify({"v": v})

    @decorator("/default")
    @ValidateParameters()
    def decorator_default(
            n_opt: Simple = ParamType(default={"id": 1, "name": "Bob", "timestamp": datetime.datetime(2025, 11, 18, 0, 0)}, list_disable_query_csv=True),
            opt: Optional[Simple] = ParamType(default={"id": 2, "name": "Billy", "timestamp": datetime.datetime(2025, 11, 18, 5, 30)}, list_disable_query_csv=True)
    ):
        assert type(n_opt) is dict
        assert "id" in n_opt and "name" in n_opt and "timestamp" in n_opt
        assert type(n_opt["id"]) is int
        assert type(n_opt["name"]) is str
        assert type(n_opt["timestamp"]) is datetime.datetime
        if opt is not None:
            assert type(opt) is dict
            assert "id" in opt and "name" in opt and "timestamp" in opt
            assert type(opt["id"]) is int
            assert type(opt["name"]) is str
            assert type(opt["timestamp"]) is datetime.datetime
            opt["timestamp"] = opt["timestamp"].isoformat()
        n_opt["timestamp"] = n_opt["timestamp"].isoformat()
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_name_short(v):
        assert type(v) is dict
        assert "name" in v
        return len(v["name"]) <= 4
    
    @decorator("/func")
    @ValidateParameters()
    def func(v: Simple = ParamType(func=is_name_short, list_disable_query_csv=True)):
        assert type(v) is dict
        assert "id" in v and "name" in v and "timestamp" in v
        assert type(v["id"]) is int
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        assert len(v["name"]) <= 4
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    json_schema = {
        "type": "object",
        "required": ["id", "name", "timestamp"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "last_name": {"type": "string"},
        }
    }

    @decorator("/json_schema")
    @ValidateParameters()
    def json_schema(v: SimpleFunc = ParamType(json_schema=json_schema, list_disable_query_csv=True)):
        assert type(v) is dict
        assert "id" in v and "name" in v and "timestamp" in v
        assert type(v["id"]) is int
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    class SimpleNotRequired(TypedDict):
        id: NotRequired[int]
        name: str
        timestamp: datetime.datetime

    @decorator("/not_required")
    @ValidateParameters()
    def not_required(v: SimpleNotRequired = ParamType(list_disable_query_csv=True)):
        assert type(v) is dict
        assert "name" in v and "timestamp" in v
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        if "id" in v:
            assert type(v["id"]) is int
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    class SimpleRequired(TypedDict, total=False):
        id: int
        name: Required[str]
        timestamp: Required[datetime.datetime]

    @decorator("/required")
    @ValidateParameters()
    def required(v: SimpleRequired = ParamType(list_disable_query_csv=True)):
        assert type(v) is dict
        assert "name" in v and "timestamp" in v
        assert type(v["name"]) is str
        assert type(v["timestamp"]) is datetime.datetime
        if "id" in v:
            assert type(v["id"]) is int
        v["timestamp"] = v["timestamp"].isoformat()
        return jsonify({"v": v})

    class Coord(TypedDict):
        x: float
        y: float
        z: float
        id: NotRequired[int]

    class Complex(TypedDict):
        children: list[Simple]
        left: Coord
        right: Coord
        name: str

    @decorator("/complex")
    @ValidateParameters()
    def complex(v: Complex = ParamType(list_disable_query_csv=True)):
        assert type(v) is dict
        assert "children" in v and "left" in v and "right" in v and "name" in v
        assert type(v["name"]) is str
        assert type(v["left"]) is dict
        assert type(v["right"]) is dict
        assert type(v["children"]) is list
        new_children = []
        for ele in v["children"]:
            assert type(v) is dict
            assert "id" in ele and "name" in ele and "timestamp" in ele
            assert type(ele["id"]) is int
            assert type(ele["name"]) is str
            assert type(ele["timestamp"]) is datetime.datetime
            ele["timestamp"] = ele["timestamp"].isoformat()
            new_children.append(ele)
        v["children"] = new_children
        assert "x" in v["left"] and "y" in v["left"] and "z" in v["left"]
        assert type(v["left"]["x"]) is float
        assert type(v["left"]["y"]) is float
        assert type(v["left"]["z"]) is float
        if "id" in v["left"]:
            assert type(id) is int
        assert "x" in v["right"] and "y" in v["right"] and "z" in v["right"]
        assert type(v["right"]["x"]) is float
        assert type(v["right"]["y"]) is float
        assert type(v["right"]["z"]) is float
        if "id" in v["right"]:
            assert type(id) is int
        return jsonify({"v": v})

    return typeddict_bp

