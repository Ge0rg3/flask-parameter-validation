import datetime
from typing import Optional, List, Union

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter


def get_list_blueprint(ParamType: type[Parameter], bp_name: str, http_verb: str) -> Blueprint:
    list_bp = Blueprint(bp_name, __name__, url_prefix="/list")
    decorator = getattr(list_bp, http_verb)

    # List not currently supported by Route
    # def path(base: str, route_additions: str) -> str:
    #     return base + (route_additions if ParamType is Route else "")

    @decorator("/req_str")
    @ValidateParameters()
    def req_str(v: List[str] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is str
        return jsonify({"v": v})

    @decorator("/req_int")
    @ValidateParameters()
    def req_int(v: List[int] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is int
        return jsonify({"v": v})

    @decorator("/req_bool")
    @ValidateParameters()
    def req_bool(v: List[bool] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is bool
        return jsonify({"v": v})

    # List[Union[]] not currently supported
    # @decorator("/req_union")
    # @ValidateParameters()
    # def req_union(v: List[Union[int, float]] = ParamType()):
    #     assert type(v) is list
    #     assert type(v[0]) is int
    #     assert type(v[1]) is float
    #     return jsonify({"v": v})

    @decorator("/req_datetime")
    @ValidateParameters()
    def req_datetime(v: List[datetime.datetime] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is datetime.datetime
        v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/req_date")
    @ValidateParameters()
    def req_date(v: List[datetime.date] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is datetime.date
        v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/req_time")
    @ValidateParameters()
    def req_time(v: List[datetime.time] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is datetime.time
        v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/optional")
    @ValidateParameters()
    def optional(v: Optional[List[str]] = ParamType()):
        return jsonify({"v": v})

    @decorator("/default")
    @ValidateParameters()
    def default(
            n_opt: List[str] = ParamType(default=["a", "b"]),
            opt: Optional[List[int]] = ParamType(default=[0, 1])
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })

    def is_len_even(v):
        assert type(v) is list
        return len(v) % 2 == 0

    @decorator("/func")
    @ValidateParameters()
    def func(v: List[float] = ParamType(func=is_len_even)):
        return jsonify({"v": v})

    @decorator("/min_list_length")
    @ValidateParameters()
    def min_list_length(v: List[str] = ParamType(min_list_length=3)):
        return jsonify({"v": v})

    @decorator("/max_list_length")
    @ValidateParameters()
    def max_list_length(v: List[str] = ParamType(max_list_length=3)):
        return jsonify({"v": v})

    return list_bp
