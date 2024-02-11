from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_str_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    str_bp = Blueprint(bp_name, __name__, url_prefix="/str")
    decorator = getattr(str_bp, http_verb)

    @decorator("/required")
    @ValidateParameters()
    def required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")
    @ValidateParameters()
    def default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @decorator("/min_str_length")
    @ValidateParameters()
    def min_str_length(
            v: str = ParamType(min_str_length=1)
    ):
        return jsonify({"v": v})

    @decorator("/max_str_length")
    @ValidateParameters()
    def max_str_length(
            v: str = ParamType(max_str_length=1)
    ):
        return jsonify({"v": v})

    @decorator("/whitelist")
    @ValidateParameters()
    def whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator("/blacklist")
    @ValidateParameters()
    def blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator("/pattern")
    @ValidateParameters()
    def pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})

    def is_digit(v):
        return v.isdigit()

    @decorator("/func")
    @ValidateParameters()
    def func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/alias")
    @ValidateParameters()
    def alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})

    return str_bp
