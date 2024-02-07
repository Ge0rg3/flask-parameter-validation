from flask import Blueprint

from flask_parameter_validation.test.testing_blueprints.query_str import query_str_blueprint

query_blueprint = Blueprint('query', __name__, url_prefix="/query")

query_blueprint.register_blueprint(query_str_blueprint)
