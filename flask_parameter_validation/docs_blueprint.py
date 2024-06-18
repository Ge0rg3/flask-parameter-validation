import json
import warnings
from typing import Optional
from enum import Enum
import flask
from flask import Blueprint, current_app, jsonify
from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.exceptions.exceptions import ConfigurationError
import re

docs_blueprint = Blueprint(
    "docs", __name__, url_prefix="/docs", template_folder="./templates"
)


def get_route_docs():
    """
    Generate documentation for all Flask routes that use the ValidateParameters decorator.
    Returns a list of dictionaries, each containing documentation for a particular route.
    """
    docs = []
    for rule in current_app.url_map.iter_rules():  # Iterate through all Flask Routes
        rule_func = current_app.view_functions[
            rule.endpoint
        ]  # Get the associated function
        fn_docs = get_function_docs(rule_func)
        if fn_docs:
            fn_docs["rule"] = str(rule)
            fn_docs["methods"] = [str(method) for method in rule.methods]
            docs.append(fn_docs)
    return docs


def get_function_docs(func):
    """
    Get documentation for a specific function that uses the ValidateParameters decorator.
    Returns a dictionary containing documentation details, or None if the decorator is not used.
    """
    fn_list = ValidateParameters().get_fn_list()
    for fsig, fdocs in fn_list.items():
        if hasattr(func, "__fpv_discriminated_sig__") and func.__fpv_discriminated_sig__ == fsig:
            return {
                "docstring": format_docstring(fdocs.get("docstring")),
                "decorators": fdocs.get("decorators"),
                "args": extract_argument_details(fdocs),
                "deprecated": fdocs.get("deprecated"),
                "responses": fdocs.get("openapi_responses"),
            }
    return None


def format_docstring(docstring):
    """
    Format a function's docstring for HTML display.
    """
    if not docstring:
        return None

    docstring = docstring.strip().replace("\n", "<br/>")
    return docstring.replace("    ", "&nbsp;" * 4)


def extract_argument_details(fdocs):
    """
    Extract details about a function's arguments, including type hints and ValidateParameters details.
    """
    args_data = {}
    for idx, arg_name in enumerate(fdocs["argspec"].args):
        arg_data = {
            "name": arg_name,
            "type": get_arg_type_hint(fdocs, arg_name),
            "loc": get_arg_location(fdocs, idx),
            "loc_args": get_arg_location_details(fdocs, idx),
        }
        args_data.setdefault(arg_data["loc"], []).append(arg_data)
    return args_data


def get_arg_type_hint(fdocs, arg_name):
    """
    Extract the type hint for a specific argument.
    """
    arg_type = fdocs["argspec"].annotations[arg_name]
    def recursively_resolve_type_hint(type_to_resolve):
        if hasattr(type_to_resolve, "__name__"):  # In Python 3.9, Optional and Union do not have __name__
            type_base_name = type_to_resolve.__name__
        elif hasattr(type_to_resolve, "_name") and type_to_resolve._name is not None:
            # In Python 3.9, _name exists on list[whatever] and has a non-None value
            type_base_name = type_to_resolve._name
        else:
            # But, in Python 3.9, Optional[whatever] has _name of None - but its __origin__ is Union
            type_base_name = type_to_resolve.__origin__._name
        if hasattr(type_to_resolve, "__args__"):
            return (
                f"{type_base_name}[{', '.join([recursively_resolve_type_hint(a) for a in type_to_resolve.__args__])}]"
            )
        return type_base_name
    return recursively_resolve_type_hint(arg_type)


def get_arg_location(fdocs, idx):
    """
    Determine where in the request the argument comes from (e.g., Route, Json, Query).
    """
    return type(fdocs["argspec"].defaults[idx]).__name__


def get_arg_location_details(fdocs, idx):
    """
    Extract additional details about the location of an argument in the request.
    """
    loc_details = {}
    location = fdocs["argspec"].defaults[idx]
    for param, value in location.__dict__.items():
        if value is not None:
            if callable(value):
                loc_details[param] = f"{value.__module__}.{value.__name__}"
            elif issubclass(type(value), Enum):
                loc_details[param] = f"{type(value).__name__}.{value.name}: "
                if issubclass(type(value), int):
                    loc_details[param] += f"{value.value}"
                elif issubclass(type(value), str):
                    loc_details[param] += f"'{value.value}'"
                else:
                    loc_details[param] = f"FPV: Unsupported Enum type"
            elif type(value).__name__ == 'time':
                loc_details[param] = value.isoformat()
            elif param == 'sources':
                loc_details[param] = [type(source).__name__ for source in value]
            else:
                loc_details[param] = value
    return loc_details


@docs_blueprint.app_template_filter()
def http_badge_bg(http_method):
    """
    Provide a color badge for various HTTP methods.
    """
    color_map = {"GET": "bg-primary", "POST": "bg-success", "DELETE": "bg-danger"}
    return color_map.get(http_method, "bg-warning")


@docs_blueprint.route("/")
def docs_html():
    """
    Render the documentation as an HTML page.
    """
    config = flask.current_app.config
    return flask.render_template(
        "fpv_default_docs.html",
        site_name=config.get("FPV_DOCS_SITE_NAME", "Site"),
        docs=get_route_docs(),
        custom_blocks=config.get("FPV_DOCS_CUSTOM_BLOCKS", []),
        default_theme=config.get("FPV_DOCS_DEFAULT_THEME", "light"),
    )


@docs_blueprint.route("/json")
def docs_json():
    """
    Provide the documentation as a JSON response.
    """
    config = flask.current_app.config
    return jsonify(
        {
            "site_name": config.get("FPV_DOCS_SITE_NAME", "Site"),
            "docs": get_route_docs(),
            "custom_blocks": config.get("FPV_DOCS_CUSTOM_BLOCKS", []),
            "default_theme": config.get("FPV_DOCS_DEFAULT_THEME", "light"),
        }
    )


def fpv_error(message):
    return jsonify({"error": message})


def parameter_required(param):
    if param["type"].startswith("Optional["):
        return False
    elif "default" in param["loc_args"]:
        return False
    return True

def generate_json_schema_helper(param, param_type, parent_group=None):
    match = re.match(r'(\w+)\[([\w\[\] ,.]+)]', param_type)
    if match:
        type_group = match.group(1)
        type_params = match.group(2)
        return generate_json_schema_helper(param, type_params, parent_group=type_group)
    elif "|" in param_type and "[" not in param_type:  # Handle Union shorthand as Union
        return generate_json_schema_helper(param, f"Union[{param_type.replace('|', ',')}]", parent_group=parent_group)
    else:
        schemas = []
        param_types = [param_type]
        if parent_group in ["Union", "Optional"]:
            if "," in param_type:
                param_types = [p.strip() for p in param_type.split(",")]
        for p in param_types:
            print(f"{param['name']}: {p}")
            subschema = {}
            if p == "str":
                subschema["type"] = "string"
                if "min_str_length" in param["loc_args"]:
                    subschema["minLength"] = param["loc_args"]["min_str_length"]
                if "max_str_length" in param["loc_args"]:
                    subschema["maxLength"] = param["loc_args"]["max_str_length"]
                # TODO: Is it possible to make this work with whitelist, blacklist and pattern simultaneously?
            elif p == "int":
                subschema["type"] = "integer"
                if "min_int" in param["loc_args"]:
                    subschema["minimum"] = param["loc_args"]["min_int"]
                if "max_int" in param["loc_args"]:
                    subschema["maximum"] = param["loc_args"]["max_int"]
            elif p == "bool":
                subschema["type"] = "boolean"
            elif p == "float":
                subschema["type"] = "number"
            elif p in ["datetime", "datetime.datetime"]:
                subschema["type"] = "string"
                subschema["format"] = "date-time"
                if "datetime_format" in param["loc_args"]:
                    warnings.warn("datetime_format cannot be translated to JSON Schema, please use ISO8601 date-time",
                                  Warning, stacklevel=2)
            elif p in ["date", "datetime.date"]:
                subschema["type"] = "string"
                subschema["format"] = "date"
            elif p in ["time", "datetime.time"]:
                subschema["type"] = "string"
                subschema["format"] = "time"
            elif p == "dict":
                subschema["type"] = "object"
            elif p in ["None", "NoneType"]:
                subschema["type"] = "null"
            else:
                print(f"Unexpected type: {p}")
            schemas.append(subschema)
        if len(schemas) == 1 and parent_group is None:
            return schemas[0]
        elif parent_group in ["Optional", "Union"]:
            return {"oneOf": schemas}
        elif parent_group == "List":
            schema = {"type": "array", "items": schemas[0]}
            if "min_list_length" in param["loc_args"]:
                schema["minItems"] = param["loc_args"]["min_list_length"]
            if "max_list_length" in param["loc_args"]:
                schema["maxItems"] = param["loc_args"]["max_list_length"]
            return schema
        else:
            print(f"Unexpected situation: {param_type}, {parent_group}")


def generate_json_schema_for_parameter(param):
    return generate_json_schema_helper(param, param["type"])


def generate_json_schema_for_parameters(params):
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    for p in params:
        schema_parameter_name = p["name"] if "alias" not in p["loc_args"] else p["loc_args"]["alias"]
        if "json_schema" in p["loc_args"]:
            schema["properties"][schema_parameter_name] = p["loc_args"]["json_schema"]
        else:
            schema["properties"][schema_parameter_name] = generate_json_schema_for_parameter(p)
        if parameter_required(p):
            schema["required"].append(schema_parameter_name)
    return schema

def generate_openapi_paths_object():
    oapi_paths = {}
    for route in get_route_docs():
        oapi_path_route = re.sub(r'<(\w+):(\w+)>', r'{\2}', route['rule'])
        oapi_path_route = re.sub(r'<(\w+)>', r'{\1}', oapi_path_route)
        print(f"Adding {route['rule']} to paths as {oapi_path_route}")
        oapi_path_item = {}
        oapi_operation = {}  # tags, summary, description, externalDocs, operationId, parameters, requestBody, responses, callbacks, deprecated, security, servers
        oapi_parameters = []
        oapi_request_body = {"content": {}}
        for arg_loc in route["args"]:
            if arg_loc == "Form":
                oapi_request_body["content"]["application/x-www-form-urlencoded"] = {
                    "schema": generate_json_schema_for_parameters(route["args"][arg_loc])}
            elif arg_loc == "Json":
                oapi_request_body["content"]["application/json"] = {
                    "schema": generate_json_schema_for_parameters(route["args"][arg_loc])}
            elif arg_loc == "File":  # See https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#considerations-for-file-uploads
                for arg in route["args"][arg_loc]:
                    if "content_types" in arg["loc_args"]:
                        for content_type in arg["loc_args"]["content_types"]:
                            oapi_request_body["content"][content_type] = {}
                    else:
                        oapi_request_body["content"]["application/octet-stream"] = {}
            elif arg_loc in ["Route", "Query"]:
                for arg in route["args"][arg_loc]:
                    if "alias" in arg["loc_args"]:
                        oapi_path_route = oapi_path_route.replace(f'{{{arg["name"]}}}',
                                                                  f'{{{arg["loc_args"]["alias"]}}}')
                    schema_arg_name = arg["name"] if "alias" not in arg["loc_args"] else arg["loc_args"]["alias"]
                    if arg_loc == "Query" or (arg_loc == "Route" and f"{{{schema_arg_name}}}" in oapi_path_route):
                        parameter = {
                            "name": schema_arg_name,
                            "in": "path" if arg_loc == "Route" else "query",
                            "required": True if arg_loc == "Route" else parameter_required(arg),
                            "schema": arg["loc_args"]["json_schema"] if "json_schema" in arg[
                                "loc_args"] else generate_json_schema_for_parameter(arg),
                        }
                        if "deprecated" in arg["loc_args"] and arg["loc_args"]["deprecated"]:
                            parameter["deprecated"] = arg["loc_args"]["deprecated"]
                        oapi_parameters.append(parameter)
        if len(oapi_parameters) > 0:
            oapi_operation["parameters"] = oapi_parameters
        if len(oapi_request_body["content"].keys()) > 0:
            oapi_operation["requestBody"] = oapi_request_body
        print(route["decorators"])
        for decorator in route["decorators"]:
            for partial_decorator in ["@warnings.deprecated", "@deprecated"]:  # Support for PEP 702 in Python 3.13
                if partial_decorator in decorator:
                    oapi_operation["deprecated"] = True
        if route["deprecated"]:  # Fallback on kwarg passed to @ValidateParameters()
            oapi_operation["deprecated"] = route["deprecated"]
        if route["responses"]:
            oapi_operation["responses"] = route["responses"]
        for method in route["methods"]:
            if method not in ["OPTIONS", "HEAD"]:
                oapi_path_item[method.lower()] = oapi_operation
        if oapi_path_route in oapi_paths:
            oapi_paths[oapi_path_route] = oapi_paths[oapi_path_route] | oapi_path_item
        else:
            oapi_paths[oapi_path_route] = oapi_path_item
    return oapi_paths



@docs_blueprint.route("/openapi")
def docs_openapi():
    """
    Provide the documentation in OpenAPI format
    """
    config = flask.current_app.config
    if not config.get("FPV_OPENAPI_ENABLE", False):
        return fpv_error("FPV_OPENAPI_ENABLE is not set, and defaults to False")

    supported_versions = ["3.1.0"]
    openapi_base = config.get("FPV_OPENAPI_BASE", {"openapi": None})
    if openapi_base["openapi"] not in supported_versions:
        return fpv_error(f"Flask-Parameter-Validation only supports OpenAPI {', '.join(supported_versions)}, {openapi_base['openapi']} provided")
    if "paths" in openapi_base:
        return fpv_error(f"Flask-Parameter-Validation will overwrite the paths value of FPV_OPENAPI_BASE")
    openapi_paths = generate_openapi_paths_object()
    openapi_document = json.loads(json.dumps(openapi_base))
    openapi_document["paths"] = openapi_paths
    return jsonify(openapi_document)
