from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_bool_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    bool_bp = Blueprint(bp_name, __name__, url_prefix="/bool")
    decorator = getattr(bool_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: bool = ParamType()):
        assert type(v) is bool
        return jsonify({"v": v})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: bool = ParamType()):
        assert type(v) is bool
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: bool = ParamType()):
        assert type(v) is bool
        return jsonify({"v": v})


    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[bool] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: bool = ParamType(default=False),
            opt: Optional[bool] = ParamType(default=True)
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_true(v):  # This shouldn't really _need_ to be tested for, but it's possible for a user to do, so ¯\_(ツ)_/¯
        assert type(v) is bool
        return v

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: bool = ParamType(func=is_true)):
        return jsonify({"v": v})

    return bool_bp
