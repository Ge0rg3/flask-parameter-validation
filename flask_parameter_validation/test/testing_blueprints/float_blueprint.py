from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_float_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    float_bp = Blueprint(bp_name, __name__, url_prefix="/float")
    decorator = getattr(float_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: float = ParamType()):
        assert type(v) is float
        return jsonify({"v": v})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: float = ParamType()):
        assert type(v) is float
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: float = ParamType()):
        assert type(v) is float
        return jsonify({"v": v})


    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[float] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: float = ParamType(default=2.3),
            opt: Optional[float] = ParamType(default=3.4)
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_approx_pi(v):
        assert type(v) is float
        return round(v, 2) == 3.14

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: float = ParamType(func=is_approx_pi)):
        return jsonify({"v": v})

    @decorator(path("/json_schema", "/<v>"))
    @ValidateParameters()
    def json_schema(v: float = ParamType(json_schema={"type": "number", "multipleOf": 0.01})):
        return jsonify({"v": v})

    return float_bp
