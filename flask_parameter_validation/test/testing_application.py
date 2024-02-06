from typing import Optional

from flask import Flask, jsonify

from flask_parameter_validation import ValidateParameters, Query

def create_app():
    app = Flask(__name__)

    @app.get("/query/required_str")
    @ValidateParameters()
    def query_required_str(value: str = Query()):
        return jsonify({"value": value})

    @app.get("/query/optional_str")
    @ValidateParameters()
    def query_optional_str(value: Optional[str] = Query()):
        return jsonify({"value": value})

    @app.get("/query/str_default")
    @ValidateParameters()
    def query_str_default(
            not_optional: str = Query(default="not_optional"),
            optional: Optional[str] = Query(default="optional")
    ):
        return jsonify({
            "not_optional": not_optional,
            "optional": optional
        })

    @app.get("/query/str_min_str_length")
    @ValidateParameters()
    def query_str_min_str_length(
            v: str = Query(min_str_length=1)
    ):
        return jsonify({"v": v})

    return app