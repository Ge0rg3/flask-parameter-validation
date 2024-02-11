import datetime
from typing import Optional, Union

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_union_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    union_bp = Blueprint(bp_name, __name__, url_prefix="/union")
    decorator = getattr(union_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: Union[bool, int] = ParamType()):
        assert type(v) is bool or type(v) is int
        return jsonify({"v": v})

    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[Union[bool, int]] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: Union[bool, int] = ParamType(default=True),
            opt: Optional[Union[bool, int]] = ParamType(default=5)
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_truthy(v):
        assert type(v) is bool or type(v) is int
        if v:
            return True
        return False

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: Union[bool, int] = ParamType(func=is_truthy)):
        return jsonify({"v": v})

    return union_bp