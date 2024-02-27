import datetime
from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_datetime_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    datetime_bp = Blueprint(bp_name, __name__, url_prefix="/datetime")
    decorator = getattr(datetime_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: datetime.datetime = ParamType()):
        assert type(v) is datetime.datetime
        return jsonify({"v": v.isoformat()})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: datetime.datetime = ParamType()):
        assert type(v) is datetime.datetime
        return jsonify({"v": v.isoformat()})
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: datetime.datetime = ParamType()):
        assert type(v) is datetime.datetime
        return jsonify({"v": v.isoformat()})


    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[datetime.datetime] = ParamType()):
        if v:
            return jsonify({"v": v.isoformat()})
        return jsonify({"v": None})

    @decorator("/default")  # Route not supported by default
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

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: datetime.datetime = ParamType(func=is_in_february)):
        return jsonify({"v": v.isoformat()})

    @decorator(path("/datetime_format", "/<path:v>"))  # Using path because test format contains /
    @ValidateParameters()
    def dformat(v: datetime.datetime = ParamType(datetime_format="%m/%d/%Y %I:%M %p")):
        return jsonify({"v": v.isoformat()})

    return datetime_bp
