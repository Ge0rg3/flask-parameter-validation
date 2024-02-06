from flask import Flask, jsonify

from flask_parameter_validation import ValidateParameters, Query

def create_app():
    app = Flask(__name__)

    @app.get("/query/str")
    @ValidateParameters()
    def query_str(value: str = Query()):
        return jsonify({"value": value})

    return app