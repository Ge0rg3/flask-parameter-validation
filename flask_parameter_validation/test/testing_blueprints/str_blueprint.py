from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


def get_str_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    str_bp = Blueprint(bp_name, __name__, url_prefix="/str")
    decorator = getattr(str_bp, http_verb)

    def path(base: str, route_additions: str) -> str:
        return base + (route_additions if ParamType is Route else "")

    @decorator(path("/required", "/<v>"))
    @ValidateParameters()
    def required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/optional")  # Route not currently supported by Optional
    @ValidateParameters()
    def optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")  # Route not currently supported by default
    @ValidateParameters()
    def default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    @decorator(path("/min_str_length", "/<v>"))
    @ValidateParameters()
    def min_str_length(
            v: str = ParamType(min_str_length=2)
    ):
        return jsonify({"v": v})

    @decorator(path("/max_str_length", "/<v>"))
    @ValidateParameters()
    def max_str_length(
            v: str = ParamType(max_str_length=2)
    ):
        return jsonify({"v": v})

    @decorator(path("/whitelist", "/<v>"))
    @ValidateParameters()
    def whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator(path("/blacklist", "/<v>"))
    @ValidateParameters()
    def blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})

    @decorator(path("/pattern", "/<v>"))
    @ValidateParameters()
    def pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})

    def is_digit(v):
        return v.isdigit()

    @decorator(path("/func", "/<v>"))
    @ValidateParameters()
    def func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})

    @decorator("/alias")  # Route not currently supported by alias
    @ValidateParameters()
    def alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})

    # Test Parent Decorators
    
    @decorator(path("/decorator/required", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})
    
    @decorator("/decorator/optional")  # Route not currently supported by Optional
    @dummy_decorator
    @ValidateParameters()
    def decorator_optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})
    
    @decorator("/decorator/default")  # Route not currently supported by default
    @dummy_decorator
    @ValidateParameters()
    def decorator_default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })
    
    @decorator(path("/decorator/min_str_length", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_min_str_length(
            v: str = ParamType(min_str_length=2)
    ):
        return jsonify({"v": v})
    
    @decorator(path("/decorator/max_str_length", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_max_str_length(
            v: str = ParamType(max_str_length=2)
    ):
        return jsonify({"v": v})
    
    @decorator(path("/decorator/whitelist", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/decorator/blacklist", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/decorator/pattern", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/decorator/func", "/<v>"))
    @dummy_decorator
    @ValidateParameters()
    def decorator_func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})
    
    @decorator("/decorator/alias")  # Route not currently supported by alias
    @dummy_decorator
    @ValidateParameters()
    def decorator_alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})
    
    # Test Parent Decorators Async
    
    @decorator(path("/async_decorator/required", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_required(v: str = ParamType()):
        assert type(v) is str
        return jsonify({"v": v})
    
    @decorator("/async_decorator/optional")  # Route not currently supported by Optional
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_optional(v: Optional[str] = ParamType()):
        return jsonify({"v": v})
    
    @decorator("/async_decorator/default")  # Route not currently supported by default
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_default(
            n_opt: str = ParamType(default="not_optional"),
            opt: Optional[str] = ParamType(default="optional")
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })
    
    @decorator(path("/async_decorator/min_str_length", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_min_str_length(
            v: str = ParamType(min_str_length=2)
    ):
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/max_str_length", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_max_str_length(
            v: str = ParamType(max_str_length=2)
    ):
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/whitelist", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_whitelist(
            v: str = ParamType(whitelist="ABC123")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/blacklist", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_blacklist(
            v: str = ParamType(blacklist="ABC123")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/pattern", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_pattern(
            v: str = ParamType(pattern="\\w{3}\\d{3}")
    ):
        return jsonify({"v": v})
    
    @decorator(path("/async_decorator/func", "/<v>"))
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_func(
            v: str = ParamType(func=is_digit)
    ):
        assert type(v) is str
        return jsonify({"v": v})
    
    @decorator("/async_decorator/alias")  # Route not currently supported by alias
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_alias(
            value: str = ParamType(alias="v")
    ):
        return jsonify({"value": value})

    return str_bp