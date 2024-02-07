from typing import Optional

from flask import Flask, jsonify

from flask_parameter_validation import ValidateParameters, Query
from flask_parameter_validation.test.testing_blueprints.query import query_blueprint


def create_app():
    app = Flask(__name__)

    app.register_blueprint(query_blueprint)

    return app