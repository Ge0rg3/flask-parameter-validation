from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Query

query_float_blueprint = Blueprint('query_float', __name__, url_prefix="/float")


@query_float_blueprint.get("/required")
@ValidateParameters()
def query_required_float(v: float = Query()):
    assert type(v) is float
    return jsonify({"v": v})


@query_float_blueprint.get("/optional")
@ValidateParameters()
def query_optional_float(v: Optional[float] = Query()):
    return jsonify({"v": v})


@query_float_blueprint.get("/default")
@ValidateParameters()
def query_float_default(
        n_opt: float = Query(default=2.3),
        opt: Optional[float] = Query(default=3.4)
):
    return jsonify({
        "n_opt": n_opt,
        "opt": opt
    })


def is_approx_pi(v):
    assert type(v) is float
    return round(v, 2) == 3.14


@query_float_blueprint.get("/func")
@ValidateParameters()
def query_float_func(v: float = Query(func=is_approx_pi)):
    return jsonify({"v": v})
