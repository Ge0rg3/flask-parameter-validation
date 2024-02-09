from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_float_blueprint(ParamType: type[Parameter], bp_name: str) -> Blueprint:
    float_bp = Blueprint(bp_name, __name__, url_prefix="/float")

    @float_bp.get("/required")
    @ValidateParameters()
    def required(v: float = ParamType()):
        assert type(v) is float
        return jsonify({"v": v})

    @float_bp.get("/optional")
    @ValidateParameters()
    def optional(v: Optional[float] = ParamType()):
        return jsonify({"v": v})

    @float_bp.get("/default")
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

    @float_bp.get("/func")
    @ValidateParameters()
    def func(v: float = ParamType(func=is_approx_pi)):
        return jsonify({"v": v})

    return float_bp
