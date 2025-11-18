import sys
import datetime
import uuid
from typing import Optional, List, Union, TypedDict, NotRequired, Required

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.multi_source import MultiSource


def get_multi_source_blueprint(sources, name):
    param_bp = Blueprint(name, __name__, url_prefix=f"/{name}")

    @param_bp.route("/required_bool", methods=["GET", "POST"])
    @param_bp.route("/required_bool/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_bool(v: bool = MultiSource(sources[0], sources[1])):
        assert type(v) is bool
        return jsonify({"v": v})

    @param_bp.route("/optional_bool", methods=["GET", "POST"])
    @param_bp.route("/optional_bool/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_bool(v: Optional[bool] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/required_date", methods=["GET", "POST"])
    @param_bp.route("/required_date/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_date(v: datetime.date = MultiSource(sources[0], sources[1])):
        assert type(v) is datetime.date
        return jsonify({"v": v.isoformat()})

    @param_bp.route("/optional_date", methods=["GET", "POST"])
    @param_bp.route("/optional_date/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_date(v: Optional[datetime.date] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v.isoformat() if v else v})

    @param_bp.route("/required_datetime", methods=["GET", "POST"])
    @param_bp.route("/required_datetime/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_datetime(v: datetime.datetime = MultiSource(sources[0], sources[1])):
        assert type(v) is datetime.datetime
        return jsonify({"v": v.isoformat()})

    @param_bp.route("/optional_datetime", methods=["GET", "POST"])
    @param_bp.route("/optional_datetime/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_datetime(v: Optional[datetime.datetime] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v.isoformat() if v else v})

    @param_bp.route("/required_dict", methods=["GET", "POST"])
    # Route doesn't support dict parameters
    @ValidateParameters()
    def multi_source_dict(v: dict = MultiSource(sources[0], sources[1])):
        assert type(v) is dict
        return jsonify({"v": v})

    @param_bp.route("/optional_dict", methods=["GET", "POST"])
    # Route doesn't support dict parameters
    @ValidateParameters()
    def multi_source_optional_dict(v: Optional[dict] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/required_float", methods=["GET", "POST"])
    @param_bp.route("/required_float/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_float(v: float = MultiSource(sources[0], sources[1])):
        assert type(v) is float
        return jsonify({"v": v})

    @param_bp.route("/optional_float", methods=["GET", "POST"])
    @param_bp.route("/optional_float/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_float(v: Optional[float] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/required_int", methods=["GET", "POST"])
    @param_bp.route("/required_int/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_int(v: int = MultiSource(sources[0], sources[1])):
        assert type(v) is int
        return jsonify({"v": v})

    @param_bp.route("/optional_int", methods=["GET", "POST"])
    @param_bp.route("/optional_int/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_int(v: Optional[int] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    # Only List[int] and list[dict[str, Union[str, int]]] is tested here - the other existing tests for lists should be exhaustive enough to catch issues
    @param_bp.route("/required_list", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_list(v: List[int] = MultiSource(sources[0], sources[1])):
        assert type(v) is list
        assert len(v) > 0
        assert type(v[0]) is int
        return jsonify({"v": v})

    @param_bp.route("/dict/args/str/str", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_dict_str_str(v: dict[str, str] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
        assert type(v) is dict
        for key, val in v.items():
            assert type(key) is str
            assert type(val) is str
        return jsonify({"v": v})

    @param_bp.route("/dict/args/str/union", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_dict_str_union(v: dict[str, Union[str, int]] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
        assert type(v) is dict
        for key, val in v.items():
            assert type(key) is str
            assert type(val) is str or type(val) is int
        return jsonify({"v": v})

    @param_bp.route("/dict/args/str/list", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_dict_str_list(v: dict[str, Union[list[int], bool]] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
        assert type(v) is dict
        for key, val in v.items():
            assert type(key) is str
            assert type(val) is list or type(val) is bool
            if type(val) is list:
                for ele in val:
                    assert type(ele) is int
        return jsonify({"v": v})

    @param_bp.route("/list/dict/args/str/union", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_list_dict_str_union(v: list[dict[str, Union[str, int]]] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
        assert type(v) is list
        for ele in v:
            assert type(ele) is dict
            for key, val in ele.items():
                assert type(key) is str
                assert type(val) is str or type(val) is int
        return jsonify({"v": v})

    @param_bp.route("/optional_list", methods=["GET", "POST"])
    # Route doesn't support List parameters
    @ValidateParameters()
    def multi_source_optional_list(v: Optional[List[int]] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/required_str", methods=["GET", "POST"])
    @param_bp.route("/required_str/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_str(v: str = MultiSource(sources[0], sources[1])):
        assert type(v) is str
        return jsonify({"v": v})

    @param_bp.route("/optional_str", methods=["GET", "POST"])
    @param_bp.route("/optional_str/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_str(v: Optional[str] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/required_time", methods=["GET", "POST"])
    @param_bp.route("/required_time/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_time(v: datetime.time = MultiSource(sources[0], sources[1])):
        assert type(v) is datetime.time
        return jsonify({"v": v.isoformat()})

    @param_bp.route("/optional_time", methods=["GET", "POST"])
    @param_bp.route("/optional_time/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_time(v: Optional[datetime.time] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v.isoformat() if v else v})

    @param_bp.route("/required_union", methods=["GET", "POST"])
    @param_bp.route("/required_union/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_union(v: Union[int, str] = MultiSource(sources[0], sources[1])):
        assert type(v) is int or type(v) is str
        return jsonify({"v": v})

    @param_bp.route("/optional_union", methods=["GET", "POST"])
    @param_bp.route("/optional_union/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_union(v: Optional[Union[int, str]] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/kwargs", methods=["GET", "POST"])
    @param_bp.route("/kwargs/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_kwargs(v: int = MultiSource(sources[0], sources[1], min_int=0)):
        return jsonify({"v": v})

    @param_bp.route("/required_uuid", methods=["GET", "POST"])
    @param_bp.route("/required_uuid/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_uuid(v: uuid.UUID = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    @param_bp.route("/optional_uuid", methods=["GET", "POST"])
    @param_bp.route("/optional_uuid/<v>", methods=["GET", "POST"])
    @ValidateParameters()
    def multi_source_optional_uuid(v: Optional[uuid.UUID] = MultiSource(sources[0], sources[1])):
        return jsonify({"v": v})

    if sys.version_info >= (3, 10):
        @param_bp.route("/union/3_10/required", methods=["GET", "POST"])
        @param_bp.route("/union/3_10/required/<v>", methods=["GET", "POST"])
        @ValidateParameters()
        def multi_source_3_10_union(v: bool | datetime.datetime = MultiSource(sources[0], sources[1])):
            return jsonify({"v": v.isoformat() if type(v) is datetime.datetime else v})

        @param_bp.route("/dict/args/str/3_10_union", methods=["GET", "POST"])
        # Route doesn't support Dict parameters
        @ValidateParameters()
        def multi_source_dict_str_3_10_union(v: dict[str, Union[str, int]] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
            assert type(v) is dict
            for key, val in v.items():
                assert type(key) is str
                assert type(val) is str or type(val) is int
            return jsonify({"v": v})

        @param_bp.route("/dict/args/str/list/3_10_union", methods=["GET", "POST"])
        # Route doesn't support Dict parameters
        @ValidateParameters()
        def multi_source_dict_str_list_3_10_union(v: dict[str, Union[list[int], bool]] = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
            assert type(v) is dict
            for key, val in v.items():
                assert type(key) is str
                assert type(val) is list or type(val) is bool
                if type(val) is list:
                    for ele in val:
                        assert type(ele) is int
            return jsonify({"v": v})

        class Simple(TypedDict):
            id: int
            name: str
            timestamp: datetime.datetime

        @param_bp.route("/typeddict/", methods=["GET", "POST"])
        @ValidateParameters()
        def multi_source_typeddict_normal(v: Simple = MultiSource(sources[0], sources[1], list_disable_query_csv=True)):
            assert type(v) is dict
            assert "id" in v and "name" in v and "timestamp" in v
            assert type(v["id"]) is int
            assert type(v["name"]) is str
            assert type(v["timestamp"]) is datetime.datetime
            v["timestamp"] = v["timestamp"].isoformat()
            return jsonify({"v": v})

    return param_bp
