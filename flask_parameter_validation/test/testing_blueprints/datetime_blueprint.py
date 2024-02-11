import datetime
from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_datetime_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    datetime_bp = Blueprint(bp_name, __name__, url_prefix="/datetime")
    decorator = getattr(datetime_bp, http_verb)

    @decorator("/required")
    @ValidateParameters()
    def required(v: datetime.datetime = ParamType()):
        assert type(v) is datetime.datetime
        return jsonify({"v": v.isoformat()})

    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[datetime.datetime] = ParamType()):
        if v:
            return jsonify({"v": v.isoformat()})
        return jsonify({"v": None})

    @decorator("/default")
    @ValidateParameters()
    def default(
            n_opt: datetime.datetime = ParamType(default=datetime.datetime(2024, 2, 8, 21, 48, 00)),
            opt: Optional[datetime.datetime] = ParamType(default=datetime.datetime(2024, 2, 8, 21, 49, 00))
    ):
        return jsonify({
            "n_opt": n_opt.isoformat(),
            "opt": opt.isoformat()
        })

    def is_in_february(v):
        assert type(v) is datetime.datetime
        return v.month == 2

    @decorator("/func")
    @ValidateParameters()
    def func(v: datetime.datetime = ParamType(func=is_in_february)):
        return jsonify({"v": v.isoformat()})

    @decorator("/datetime_format")
    @ValidateParameters()
    def dformat(v: datetime.datetime = ParamType(datetime_format="%m/%d/%Y %I:%M %p")):
        return jsonify({"v": v.isoformat()})

    return datetime_bp
