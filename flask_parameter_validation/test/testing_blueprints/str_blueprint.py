from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_str_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    str_bp = Blueprint(bp_name, __name__, url_prefix="/str")
    decorator = getattr(str_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/optional")  # Route not currently supported by Optional
    @ValidateParameters()
    def optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not currently supported by default
    @ValidateParameters()
    def default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @decorator(path("/min_str_length", "/<v>"))
    @ValidateParameters()
    def min_str_length(
            v: str = ParamType(min_str_length=2)
    ):
        return jsonify({"v": v})

    @decorator(path("/max_str_length", "/<v>"))
    @ValidateParameters()
    def max_str_length(
            v: str = ParamType(max_str_length=2)
    ):
        return jsonify({"v": v})

    @decorator(path("/whitelist", "/<v>"))
    @ValidateParameters()
    def whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator(path("/blacklist", "/<v>"))
    @ValidateParameters()
    def blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator(path("/pattern", "/<v>"))
    @ValidateParameters()
    def pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})

    def is_digit(v):
        return v.isdigit()

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/alias")  # Route not currently supported by alias
    @ValidateParameters()
    def alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})

    return str_bp
