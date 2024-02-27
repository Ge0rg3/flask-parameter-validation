import datetime
from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_date_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    date_bp = Blueprint(bp_name, __name__, url_prefix="/date")
    decorator = getattr(date_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: datetime.date = ParamType()):
        assert type(v) is datetime.date
        return jsonify({"v": v.isoformat()})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: datetime.date = ParamType()):
        assert type(v) is datetime.date
        return jsonify({"v": v.isoformat()})
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: datetime.date = ParamType()):
        assert type(v) is datetime.date
        return jsonify({"v": v.isoformat()})

    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[datetime.date] = ParamType()):
        if v:
            return jsonify({"v": v.isoformat()})
        return jsonify({"v": None})

    @decorator("/default")  # Route not supported by default
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

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: datetime.date = ParamType(func=is_in_q1)):
        return jsonify({"v": v.isoformat()})

    return date_bp