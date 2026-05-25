from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator

_fpv_test_openapi_responses_object = {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "v": {"type": "integer"},
                        }
                    }
                }
            }
        }
    }

def get_int_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    global _fpv_test_openapi_responses_object
    int_bp = Blueprint(bp_name, __name__, url_prefix="/int")
    decorator = getattr(int_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<int:v>"))
    @ValidateParameters(openapi_responses=_fpv_test_openapi_responses_object)
    def required(v: int = ParamType()):
        assert type(v) is int
        return jsonify({"v": v})

    @decorator(path("/decorator/required", "/<int:v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: int = ParamType()):
        assert type(v) is int
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/required", "/<int:v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: int = ParamType()):
        assert type(v) is int
        return jsonify({"v": v})

    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[int] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: int = ParamType(default=1),
            opt: Optional[int] = ParamType(default=2)
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @decorator(path("/min_int", "/<v>"))
    @ValidateParameters()
    def min_int(v: int = ParamType(min_int=0)):
        return jsonify({"v": v})

    @decorator(path("/max_int", "/<v>"))
    @ValidateParameters()
    def max_int(v: int = ParamType(max_int=0)):
        return jsonify({"v": v})

    def is_even(v):
        assert type(v) is int
        return v % 2 == 0

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: int = ParamType(func=is_even)):
        """
        Test Docstring on Route
        """
        return jsonify({"v": v})

    return int_bp
