import uuid
from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_uuid_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    uuid_bp = Blueprint(bp_name, __name__, url_prefix="/uuid")
    decorator = getattr(uuid_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: uuid.UUID = ParamType()):
        assert type(v) is uuid.UUID
        return jsonify({"v": v})

    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: uuid.UUID = ParamType()):
        assert type(v) is uuid.UUID
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: uuid.UUID = ParamType()):
        assert type(v) is uuid.UUID
        return jsonify({"v": v})

    @decorator("/optional")  # Route not supported by Optional
    @ValidateParameters()
    def optional(v: Optional[uuid.UUID] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not supported by default
    @ValidateParameters()
    def default(
            n_opt: uuid.UUID = ParamType(default="9ba0c75f-1574-4464-bd7d-760262e3ea41"),
            opt: Optional[uuid.UUID] = ParamType(default=uuid.UUID("2f01faa3-29a2-4b36-b406-2ad288fb4969"))
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_v4(v):  # This shouldn't really _need_ to be tested for, but it's possible for a user to do, so ¯\_(ツ)_/¯
        assert type(v) is uuid.UUID
        return v.version == 4

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(v: uuid.UUID = ParamType(func=is_v4)):
        return jsonify({"v": v})

    return uuid_bp
