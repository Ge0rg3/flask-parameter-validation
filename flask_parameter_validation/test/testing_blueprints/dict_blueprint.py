import datetime
from typing import Optional, List, Union

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_dict_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    dict_bp = Blueprint(bp_name, __name__, url_prefix="/dict")
    decorator = getattr(dict_bp, http_verb)

    # dict not currently supported by Route
    # def path(base: str, route_additions: str) -> str:
    #     return base + (route_additions if ParamType is Route else "")

    @decorator("/required")
    @ValidateParameters()
    def req_str(v: dict = ParamType()):
        assert type(v) is dict
        return jsonify({"v": v})

    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[dict] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")
    @ValidateParameters()
    def default(
            n_opt: dict = ParamType(default={"a": "b"}),
            opt: dict = ParamType(default={"c": "d"})
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @decorator("/decorator/default")
    @dummy_decorator
    @ValidateParameters()
    def decorator_default(
            n_opt: dict = ParamType(default={"a": "b"}),
            opt: dict = ParamType(default={"c": "d"})
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })
    
    @decorator("/async_decorator/default")
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_default(
            n_opt: dict = ParamType(default={"a": "b"}),
            opt: dict = ParamType(default={"c": "d"})
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def are_keys_lowercase(v):
        assert type(v) is dict
        for key in v.keys():
            if not key.islower():
                return False
        return True

    @decorator("/func")
    @ValidateParameters()
    def func(v: dict = ParamType(func=are_keys_lowercase)):
        return jsonify({"v": v})

    json_schema = {
        "type": "object",
        "required": ["user_id", "first_name", "last_name", "tags"],
        "properties": {
            "user_id": {"type": "integer"},
            "first_name": {"type": "string"},
            "last_name": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }

    @decorator("/json_schema")
    @ValidateParameters()
    def json_schema(v: dict = ParamType(json_schema=json_schema)):
        return jsonify({"v": v})

    return dict_bp
