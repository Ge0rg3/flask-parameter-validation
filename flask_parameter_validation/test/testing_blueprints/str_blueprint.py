from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_str_blueprint(ParamType: type[Parameter], bp_name: str) -> Blueprint:
    str_bp = Blueprint(bp_name, __name__, url_prefix="/str")

    @str_bp.get("/required")
    @ValidateParameters()
    def required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})

    @str_bp.get("/optional")
    @ValidateParameters()
    def optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})

    @str_bp.get("/default")
    @ValidateParameters()
    def default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @str_bp.get("/min_str_length")
    @ValidateParameters()
    def min_str_length(
            v: str = ParamType(min_str_length=1)
    ):
        return jsonify({"v": v})

    @str_bp.get("/max_str_length")
    @ValidateParameters()
    def max_str_length(
            v: str = ParamType(max_str_length=1)
    ):
        return jsonify({"v": v})

    @str_bp.get("/whitelist")
    @ValidateParameters()
    def whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})

    @str_bp.get("/blacklist")
    @ValidateParameters()
    def blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})

    @str_bp.get("/pattern")
    @ValidateParameters()
    def pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})

    def is_digit(v):
        return v.isdigit()

    @str_bp.get("/func")
    @ValidateParameters()
    def func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})

    @str_bp.get("/alias")
    @ValidateParameters()
    def alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})

    return str_bp
