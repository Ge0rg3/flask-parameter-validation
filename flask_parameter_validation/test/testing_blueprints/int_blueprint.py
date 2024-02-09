from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_int_blueprint(ParamType: type[Parameter], bp_name: str) -> Blueprint:
    int_bp = Blueprint(bp_name, __name__, url_prefix="/int")

    @int_bp.get("/required")
    @ValidateParameters()
    def required(v: int = ParamType()):
        assert type(v) is int
        return jsonify({"v": v})

    @int_bp.get("/optional")
    @ValidateParameters()
    def optional(v: Optional[int] = ParamType()):
        return jsonify({"v": v})

    @int_bp.get("/default")
    @ValidateParameters()
    def default(
            n_opt: int = ParamType(default=1),
            opt: Optional[int] = ParamType(default=2)
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @int_bp.get("/min_int")
    @ValidateParameters()
    def min_int(v: int = ParamType(min_int=0)):
        return jsonify({"v": v})

    @int_bp.get("/max_int")
    @ValidateParameters()
    def max_int(v: int = ParamType(max_int=0)):
        return jsonify({"v": v})

    def is_even(v):
        assert type(v) is int
        return v % 2 == 0

    @int_bp.get("/func")
    @ValidateParameters()
    def func(v: int = ParamType(func=is_even)):
        return jsonify({"v": v})

    return int_bp
