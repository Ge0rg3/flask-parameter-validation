from flask import Blueprint

from flask_parameter_validation.parameter_types.parameter import Parameter
from flask_parameter_validation.test.enums import Fruits, Binary
from flask_parameter_validation.test.testing_blueprints.bool_blueprint import get_bool_blueprint
from flask_parameter_validation.test.testing_blueprints.date_blueprint import get_date_blueprint
from flask_parameter_validation.test.testing_blueprints.datetime_blueprint import get_datetime_blueprint
from flask_parameter_validation.test.testing_blueprints.dict_blueprint import get_dict_blueprint
from flask_parameter_validation.test.testing_blueprints.enum_blueprint import get_enum_blueprint
from flask_parameter_validation.test.testing_blueprints.float_blueprint import get_float_blueprint
from flask_parameter_validation.test.testing_blueprints.int_blueprint import get_int_blueprint
from flask_parameter_validation.test.testing_blueprints.list_blueprint import get_list_blueprint
from flask_parameter_validation.test.testing_blueprints.str_blueprint import get_str_blueprint
from flask_parameter_validation.test.testing_blueprints.time_blueprint import get_time_blueprint
from flask_parameter_validation.test.testing_blueprints.union_blueprint import get_union_blueprint
from flask_parameter_validation.test.testing_blueprints.uuid_blueprint import get_uuid_blueprint
from flask_parameter_validation.test.testing_blueprints.typeddict_blueprint import get_typeddict_blueprint


def get_parameter_blueprint(ParamType: type[Parameter], bp_name: str, param_name: str, http_verb: str) -> Blueprint:
    param_bp = Blueprint(bp_name, __name__, url_prefix=f"/{param_name}")

    # typing.Optional is covered in all of the below
    param_bp.register_blueprint(get_str_blueprint(ParamType, f"{bp_name}_str", http_verb))
    param_bp.register_blueprint(get_int_blueprint(ParamType, f"{bp_name}_int", http_verb))
    param_bp.register_blueprint(get_bool_blueprint(ParamType, f"{bp_name}_bool", http_verb))
    param_bp.register_blueprint(get_float_blueprint(ParamType, f"{bp_name}_float", http_verb))
    param_bp.register_blueprint(get_list_blueprint(ParamType, f"{bp_name}_list", http_verb))
    param_bp.register_blueprint(get_union_blueprint(ParamType, f"{bp_name}_union", http_verb))
    param_bp.register_blueprint(get_datetime_blueprint(ParamType, f"{bp_name}_datetime", http_verb))
    param_bp.register_blueprint(get_date_blueprint(ParamType, f"{bp_name}_date", http_verb))
    param_bp.register_blueprint(get_time_blueprint(ParamType, f"{bp_name}_time", http_verb))
    param_bp.register_blueprint(get_dict_blueprint(ParamType, f"{bp_name}_dict", http_verb))
    param_bp.register_blueprint(get_enum_blueprint(ParamType, f"{bp_name}_str_enum", http_verb, Fruits, "str_enum"))
    param_bp.register_blueprint(get_enum_blueprint(ParamType, f"{bp_name}_int_enum", http_verb, Binary, "int_enum"))
    param_bp.register_blueprint(get_uuid_blueprint(ParamType, f"{bp_name}_uuid", http_verb))
    param_bp.register_blueprint(get_typeddict_blueprint(ParamType, f"{bp_name}_typeddict", http_verb))
    return param_bp
