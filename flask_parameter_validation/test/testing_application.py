from typing import Optional

from flask import Flask, jsonify

from flask_parameter_validation import ValidateParameters, Query, Json, Form, Route
from flask_parameter_validation.test.testing_blueprints.file_blueprint import get_file_blueprint
from flask_parameter_validation.test.testing_blueprints.parameter_blueprint import get_parameter_blueprint


def create_app():
    app = Flask(__name__)

    app.register_blueprint(get_parameter_blueprint(Query, "query", "query", "get"))
    app.register_blueprint(get_parameter_blueprint(Json, "json", "json", "post"))
    app.register_blueprint(get_parameter_blueprint(Form, "form", "form", "post"))
    app.register_blueprint(get_parameter_blueprint(Route, "route", "route", "get"))
    app.register_blueprint(get_file_blueprint("file"))
    return app