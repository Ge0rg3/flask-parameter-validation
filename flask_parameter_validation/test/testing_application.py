from typing import Optional

from flask import Flask, jsonify

from flask_parameter_validation import Query, Json, Form, Route
from flask_parameter_validation.test.testing_blueprints.file_blueprint import get_file_blueprint
from flask_parameter_validation.test.testing_blueprints.multi_source_blueprint import get_multi_source_blueprint
from flask_parameter_validation.test.testing_blueprints.parameter_blueprint import get_parameter_blueprint

multi_source_sources = [
    {"class": Query, "name": "query"},
    {"class": Json, "name": "json"},
    {"class": Form, "name": "form"},
    {"class": Route, "name": "route"}
]

def create_app():
    app = Flask(__name__)

    app.register_blueprint(get_parameter_blueprint(Query, "query", "query", "get"))
    app.register_blueprint(get_parameter_blueprint(Json, "json", "json", "post"))
    app.register_blueprint(get_parameter_blueprint(Form, "form", "form", "post"))
    app.register_blueprint(get_parameter_blueprint(Route, "route", "route", "get"))
    app.register_blueprint(get_file_blueprint("file"))
    for source_a in multi_source_sources:
        for source_b in multi_source_sources:
            if source_a["name"] != source_b["name"]:
                # There's no reason to test multi-source with two of the same source
                combined_name = f"ms_{source_a['name']}_{source_b['name']}"
                app.register_blueprint(get_multi_source_blueprint([source_a['class'], source_b['class']], combined_name))
    return app
