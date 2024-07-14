from enum import Enum
from typing import Optional, Type

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.enums import Fruits, Binary
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_enum_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str, enum: Type[Enum],
                       bp_path: str) -> Blueprint:
    enum_bp = Blueprint(bp_name, __name__, url_prefix=f"/{bp_path}")
    decorator = getattr(enum_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: enum = ParamType()):
        assert type(v) is enum
        return jsonify({"v": v.value})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: enum = ParamType()):
        assert type(v) is enum
        return jsonify({"v": v.value})

    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: enum = ParamType()):
        assert type(v) is enum
        return jsonify({"v": v.value})

    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[enum] = ParamType()):
        return jsonify({"v": v.value if v is not None else v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: enum = ParamType(default=Fruits.APPLE if enum == Fruits else Binary.ZERO),
            opt: Optional[enum] = ParamType(default=Fruits.ORANGE if enum == Fruits else Binary.ONE)
    ):
        return jsonify({
            "n_opt": n_opt.value,
            "opt": opt.value
        })

    def magic_func(v):
        if type(v) is Fruits:
            return v == Fruits.ORANGE
        elif type(v) is Binary:
            return v == Binary.ZERO
        return True  # Wouldn't usually do this, but it'll be called on

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: enum = ParamType(func=magic_func)):
        return jsonify({"v": v.value})

    return enum_bp
