import datetime
from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_date_blueprint(ParamType: type[Parameter], bp_name: str) -> Blueprint:
    date_bp = Blueprint(bp_name, __name__, url_prefix="/date")

    @date_bp.get("/required")
    @ValidateParameters()
    def required(v: datetime.date = ParamType()):
        assert type(v) is datetime.date
        return jsonify({"v": v.isoformat()})

    @date_bp.get("/optional")
    @ValidateParameters()
    def optional(v: Optional[datetime.date] = ParamType()):
        if v:
            return jsonify({"v": v.isoformat()})
        return jsonify({"v": None})

    @date_bp.get("/default")
    @ValidateParameters()
    def default(
            n_opt: datetime.date = ParamType(default=datetime.date(2024, 2, 9)),
            opt: Optional[datetime.date] = ParamType(default=datetime.date(2024, 2, 10))
    ):
        return jsonify({
            "n_opt": n_opt.isoformat(),
            "opt": opt.isoformat()
        })

    def is_in_q1(v):
        assert type(v) is datetime.date
        return v.month <= 3

    @date_bp.get("/func")
    @ValidateParameters()
    def func(v: datetime.date = ParamType(func=is_in_q1)):
        return jsonify({"v": v.isoformat()})

    return date_bp