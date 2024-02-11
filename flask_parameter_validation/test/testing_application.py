from typing import Optional

from flask import Flask, jsonify

from flask_parameter_validation import ValidateParameters, Query, Json, Form
from flask_parameter_validation.test.testing_blueprints.parameter_blueprint import get_parameter_blueprint


def create_app():
    app = Flask(__name__)

    app.register_blueprint(get_parameter_blueprint(Query, "query", "query", "get"))
    app.register_blueprint(get_parameter_blueprint(Json, "json", "json", "post"))
    app.register_blueprint(get_parameter_blueprint(Form, "form", "form", "post"))

    return app