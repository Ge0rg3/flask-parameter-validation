from typing import Optional

from flask import Blueprint, jsonify

from flask_parameter_validation import ValidateParameters, Query

query_bool_blueprint = Blueprint('query_bool', __name__, url_prefix="/bool")


@query_bool_blueprint.get("/required")
@ValidateParameters()
def query_required_bool(v: bool = Query()):
    assert type(v) is bool
    return jsonify({"v": v})


@query_bool_blueprint.get("/optional")
@ValidateParameters()
def query_optional_bool(v: Optional[bool] = Query()):
    return jsonify({"v": v})


@query_bool_blueprint.get("/default")
@ValidateParameters()
def query_bool_default(
        n_opt: bool = Query(default=False),
        opt: Optional[bool] = Query(default=True)
):
    return jsonify({
        "n_opt": n_opt,
        "opt": opt
    })


def is_true(v):  # This shouldn't really _need_ to be tested for, but it's possible for a user to do, so ¯\_(ツ)_/¯
    assert type(v) is bool
    return v


@query_bool_blueprint.get("/func")
@ValidateParameters()
def query_bool_func(v: bool = Query(func=is_true)):
    return jsonify({"v": v})
