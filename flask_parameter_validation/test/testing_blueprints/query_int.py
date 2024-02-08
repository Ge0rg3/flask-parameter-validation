from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Query

query_int_blueprint = Blueprint('query_int', __name__, url_prefix="/int")


@query_int_blueprint.get("/required")
@ValidateParameters()
def query_required_int(v: int = Query()):
    return jsonify({"v": v})


@query_int_blueprint.get("/optional")
@ValidateParameters()
def query_optional_int(v: Optional[int] = Query()):
    return jsonify({"v": v})


@query_int_blueprint.get("/default")
@ValidateParameters()
def query_int_default(
        n_opt: int = Query(default=1),
        opt: Optional[int] = Query(default=2)
):
    return jsonify({
        "n_opt": n_opt,
        "opt": opt
    })


@query_int_blueprint.get("/min_int")
@ValidateParameters()
def query_min_int(v: int = Query(min_int=0)):
    return jsonify({"v": v})


@query_int_blueprint.get("/max_int")
@ValidateParameters()
def query_max_int(v: int = Query(max_int=0)):
    return jsonify({"v": v})


def is_even(v):
    print(type(v))
    return v % 2 == 0


@query_int_blueprint.get("/func")
@ValidateParameters()
def query_int_func(v: int = Query(func=is_even)):
    return jsonify({"v": v})
