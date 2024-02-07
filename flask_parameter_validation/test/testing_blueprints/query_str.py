from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Query

query_str_blueprint = Blueprint('query_str', __name__, url_prefix="/str")


@query_str_blueprint.get("/required")
@ValidateParameters()
def query_required_str(v: str = Query()):
    return jsonify({"v": v})


@query_str_blueprint.get("/optional")
@ValidateParameters()
def query_optional_str(v: Optional[str] = Query()):
    return jsonify({"v": v})


@query_str_blueprint.get("/default")
@ValidateParameters()
def query_str_default(
        n_opt: str = Query(default="not_optional"),
        opt: Optional[str] = Query(default="optional")
):
    return jsonify({
        "n_opt": n_opt,
        "opt": opt
    })


@query_str_blueprint.get("/min_str_length")
@ValidateParameters()
def query_str_min_str_length(
        v: str = Query(min_str_length=1)
):
    return jsonify({"v": v})


@query_str_blueprint.get("/max_str_length")
@ValidateParameters()
def query_str_max_str_length(
        v: str = Query(max_str_length=1)
):
    return jsonify({"v": v})


@query_str_blueprint.get("/whitelist")
@ValidateParameters()
def query_str_whitelist(
        v: str = Query(whitelist="ABC123")
):
    return jsonify({"v": v})


@query_str_blueprint.get("/blacklist")
@ValidateParameters()
def query_str_blacklist(
        v: str = Query(blacklist="ABC123")
):
    return jsonify({"v": v})


@query_str_blueprint.get("/pattern")
@ValidateParameters()
def query_str_pattern(
        v: str = Query(pattern="\\w{3}\\d{3}")
):
    return jsonify({"v": v})


def is_digit(v):
    return v.isdigit()


@query_str_blueprint.get("/func")
@ValidateParameters()
def query_str_func(
        v: str = Query(func=is_digit)
):
    return jsonify({"v": v})


@query_str_blueprint.get("/alias")
@ValidateParameters()
def query_str_alias(
        value: str = Query(alias="v")
):
    return jsonify({"value": value})
