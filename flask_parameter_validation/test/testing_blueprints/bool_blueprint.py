from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_bool_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    bool_bp = Blueprint(bp_name, __name__, url_prefix="/bool")
    decorator = getattr(bool_bp, http_verb)

    @decorator("/required")
    @ValidateParameters()
    def required(v: bool = ParamType()):
        assert type(v) is bool
        return jsonify({"v": v})

    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[bool] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")
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

    @decorator("/func")
    @ValidateParameters()
    def func(v: bool = ParamType(func=is_true)):
        return jsonify({"v": v})

    return bool_bp
