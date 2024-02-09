from flask import Blueprint

from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.testing_blueprints.bool_blueprint import get_bool_blueprint
from flask_parameter_validation.test.testing_blueprints.datetime_blueprint import get_datetime_blueprint
from flask_parameter_validation.test.testing_blueprints.float_blueprint import get_float_blueprint
from flask_parameter_validation.test.testing_blueprints.int_blueprint import get_int_blueprint
from flask_parameter_validation.test.testing_blueprints.str_blueprint import get_str_blueprint


def get_parameter_blueprint(ParamType: type[Parameter], bp_name: str, param_name: str) -> Blueprint:
    param_bp = Blueprint(bp_name, __name__, url_prefix=f"/{param_name}")

    # typing.Optional is covered in all of the below
    param_bp.register_blueprint(get_str_blueprint(ParamType, f"{bp_name}_str"))
    param_bp.register_blueprint(get_int_blueprint(ParamType, f"{bp_name}_int"))
    param_bp.register_blueprint(get_bool_blueprint(ParamType, f"{bp_name}_bool"))
    param_bp.register_blueprint(get_float_blueprint(ParamType, f"{bp_name}_float"))
    # TODO: typing.List
    # TODO: typing.Union
    param_bp.register_blueprint(get_datetime_blueprint(ParamType, f"{bp_name}_datetime"))
    # TODO: datetime.date
    # TODO: datetime.time
    return param_bp
