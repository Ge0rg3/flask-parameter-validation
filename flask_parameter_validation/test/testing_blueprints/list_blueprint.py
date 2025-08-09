import datetime
import uuid
from typing import Optional, List, Union

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Route
from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.enums import Binary, Fruits
from flask_parameter_validation.test.testing_blueprints.dummy_decorators import dummy_decorator, dummy_async_decorator


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
        if len(v) > 0:
            assert type(v[0]) is str
        return jsonify({"v": v})
    
    @decorator("/decorator/req_str")
    @dummy_decorator
    @ValidateParameters()
    def decorator_req_str(v: List[str] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is str
        return jsonify({"v": v})
    
    @decorator("/async_decorator/req_str")
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_req_str(v: List[str] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is str
        return jsonify({"v": v})

    @decorator("/opt_str")
    @ValidateParameters()
    def opt_str(v: Optional[List[str]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is str
        return jsonify({"v": v})

    @decorator("/disable_query_csv/unset")
    @ValidateParameters()
    def disable_query_csv_unset(v: List[str] = ParamType()):
        return jsonify({"v": v})

    @decorator("/disable_query_csv/true")
    @ValidateParameters()
    def disable_query_csv_true(v: List[str] = ParamType(list_disable_query_csv=True)):
        return jsonify({"v": v})

    @decorator("/disable_query_csv/false")
    @ValidateParameters()
    def disable_query_csv_false(v: List[str] = ParamType(list_disable_query_csv=False)):
        return jsonify({"v": v})

    @decorator("/req_int")
    @ValidateParameters()
    def req_int(v: List[int] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is int
        return jsonify({"v": v})

    @decorator("/opt_int")
    @ValidateParameters()
    def opt_int(v: Optional[List[int]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is int
        return jsonify({"v": v})

    @decorator("/req_bool")
    @ValidateParameters()
    def req_bool(v: List[bool] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is bool
        return jsonify({"v": v})

    @decorator("/opt_bool")
    @ValidateParameters()
    def opt_bool(v: Optional[List[bool]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is bool
        return jsonify({"v": v})

    @decorator("/req_float")
    @ValidateParameters()
    def req_float(v: List[float] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is float
        return jsonify({"v": v})

    @decorator("/opt_float")
    @ValidateParameters()
    def opt_float(v: Optional[List[float]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is float
        return jsonify({"v": v})

    @decorator("/req_union")
    @ValidateParameters()
    def req_union(v: List[Union[int, float]] = ParamType()):
        assert type(v) is list
        for i in v:
            assert type(i) is int or type(i) is float
        return jsonify({"v": v})

    @decorator("/req_union_everything")
    @ValidateParameters()
    def req_union_everything(v: List[Union[str, int, bool, float, datetime.datetime, datetime.date, datetime.time, dict, Fruits, Binary, uuid.UUID]] = ParamType(list_disable_query_csv=True)):
        assert type(v) is list
        assert len(v) > 0
        assert type(v[0]) is str
        assert type(v[1]) is int
        assert type(v[2]) is bool
        assert type(v[3]) is float
        assert type(v[4]) is datetime.datetime
        assert type(v[5]) is datetime.date
        assert type(v[6]) is datetime.time
        assert type(v[7]) is dict
        assert type(v[8]) is Fruits
        assert type(v[9]) is Binary
        assert type(v[10]) is uuid.UUID
        return jsonify({"v": [
            v[0], v[1], v[2], v[3],
            v[4].isoformat(),
            v[5].isoformat(),
            v[6].isoformat(),
            v[7], v[8], v[9], v[10]
        ]})

    @decorator("/req_optional")
    @ValidateParameters()
    def req_optional(v: List[Optional[str]] = ParamType()):
        assert type(v) is list
        assert len(v) > 0
        for i in v:
            assert type(i) is str or i is None
        return jsonify({"v": v})

    @decorator("/opt_union")
    @ValidateParameters()
    def opt_union(v: Optional[List[Union[int, bool]]] = ParamType()):
        assert type(v) is list or v is None
        if v:
            for i in v:
                assert type(i) is int or type(i) is bool
        return jsonify({"v": v})

    @decorator("/req_datetime")
    @ValidateParameters()
    def req_datetime(v: List[datetime.datetime] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is datetime.datetime
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/opt_datetime")
    @ValidateParameters()
    def opt_datetime(v: Optional[List[datetime.datetime]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is datetime.datetime
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/req_date")
    @ValidateParameters()
    def req_date(v: List[datetime.date] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is datetime.date
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/opt_date")
    @ValidateParameters()
    def opt_date(v: Optional[List[datetime.date]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is datetime.date
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/req_time")
    @ValidateParameters()
    def req_time(v: List[datetime.time] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is datetime.time
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/opt_time")
    @ValidateParameters()
    def opt_time(v: Optional[List[datetime.time]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is datetime.time
            v = [t.isoformat() for t in v]
        return jsonify({"v": v})

    @decorator("/req_dict")
    @ValidateParameters()
    def req_dict(v: List[dict] = ParamType(list_disable_query_csv=True)):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is dict
        return jsonify({"v": v})

    @decorator("/opt_dict")
    @ValidateParameters()
    def opt_dict(v: Optional[List[dict]] = ParamType(list_disable_query_csv=True)):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is dict
        return jsonify({"v": v})

    @decorator("/req_str_enum")
    @ValidateParameters()
    def req_str_enum(v: List[Fruits] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is Fruits
        return jsonify({"v": v})

    @decorator("/opt_str_enum")
    @ValidateParameters()
    def opt_str_enum(v: Optional[List[Fruits]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is Fruits
        return jsonify({"v": v})

    @decorator("/req_int_enum")
    @ValidateParameters()
    def req_int_enum(v: List[Binary] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is Binary
        return jsonify({"v": v})

    @decorator("/opt_int_enum")
    @ValidateParameters()
    def opt_int_enum(v: Optional[List[Binary]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is Binary
        return jsonify({"v": v})

    @decorator("/req_uuid")
    @ValidateParameters()
    def req_uuid(v: List[uuid.UUID] = ParamType()):
        assert type(v) is list
        if len(v) > 0:
            assert type(v[0]) is uuid.UUID
            v = [str(u) for u in v]
        return jsonify({"v": v})

    @decorator("/opt_uuid")
    @ValidateParameters()
    def opt_uuid(v: Optional[List[uuid.UUID]] = ParamType()):
        assert type(v) is list or v is None
        if v and len(v) > 0:
            assert type(v[0]) is uuid.UUID
            v = [str(u) for u in v]
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

    @decorator("/decorator/default")
    @dummy_decorator
    @ValidateParameters()
    def decorator_default(
            n_opt: List[str] = ParamType(default=["a", "b"]),
            opt: Optional[List[int]] = ParamType(default=[0, 1])
    ):
        return jsonify({
            "n_opt": n_opt,
            "opt": opt
        })
    
    @decorator("/async_decorator/default")
    @dummy_async_decorator
    @ValidateParameters()
    async def async_decorator_default(
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

    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["user_id", "first_name", "last_name", "tags"],
            "properties": {
                "user_id": {"type": "integer"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }

    @decorator("/json_schema")
    @ValidateParameters()
    def json_schema(v: list = ParamType(json_schema=json_schema)):
        return jsonify({"v": v})

    @decorator("/non_typing")
    @ValidateParameters()
    def non_typing(v: list[str] = ParamType()):
        assert type(v) is list
        assert type(v[0]) is str
        return jsonify({"v": v})

    @decorator("/optional_non_typing")
    @ValidateParameters()
    def optional_non_typing(v: Optional[list[str]] = ParamType()):
        return jsonify({"v": v})

    return list_bp
