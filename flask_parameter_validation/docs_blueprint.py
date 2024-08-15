import inspect
import warnings
from enum import Enum
import flask
from flask import Blueprint, current_app, jsonify
from flask_parameter_validation import ValidateParameters
import re
import copy

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
        if fsig.split(".")[-1] == func.__name__:
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
        if arg_data["type"] in ["StrEnum", "IntEnum"]:
            arg_data["enum_values"] = get_arg_enum_values(fdocs, arg_name)
        args_data.setdefault(arg_data["loc"], []).append(arg_data)
    return args_data


def get_arg_enum_values(fdocs, arg_name):
    """
    Extract the Enum values for a specific argument.
    """
    arg_type = fdocs["argspec"].annotations[arg_name]
    return list(map(lambda e: e.value, arg_type))


def get_arg_type_hint(fdocs, arg_name):
    """
    Extract the type hint for a specific argument.
    """
    arg_type = fdocs["argspec"].annotations[arg_name]
    if (inspect.isclass(arg_type) and issubclass(arg_type, Enum) and
            (issubclass(arg_type, str) or issubclass(arg_type, int))):
        if issubclass(arg_type, str):
            return "StrEnum"
        elif issubclass(arg_type, int):
            return "IntEnum"
    elif hasattr(arg_type, "__args__"):
        return (
            f"{arg_type.__name__}[{', '.join([a.__name__ for a in arg_type.__args__])}]"
        )
    return arg_type.__name__


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
    route_docs = get_route_docs()
    for route in route_docs:
        if "MultiSource" in route["args"]:
            for arg in route["args"]["MultiSource"]:
                sources = []
                for source in arg["loc_args"]["sources"]:
                    sources.append(source.__class__.__name__)
                arg["loc_args"]["sources"] = sources
    return jsonify(
        {
            "site_name": config.get("FPV_DOCS_SITE_NAME", "Site"),
            "docs": route_docs,
            "custom_blocks": config.get("FPV_DOCS_CUSTOM_BLOCKS", []),
            "default_theme": config.get("FPV_DOCS_DEFAULT_THEME", "light"),
        }
    )


def fpv_error(message):
    """ Error response helper for view functions """
    return jsonify({"error": message})


def parameter_required(param):
    """ Determine if a parameter is required, for OpenAPI Generation """
    if param["type"].startswith("Optional["):
        return False
    elif "default" in param["loc_args"]:
        return False
    return True


def generate_json_schema_helper(param, param_type, parent_group=None):
    """ Helper function for generating JSON Schema for a parameter """
    match = re.match(r'(\w+)\[([\w\[\] ,.]+)]', param_type)  # Check for type hints that take arguments (Union[])
    if match:  # Break down the type into its parent (Union) and the arguments (int, float) and recurse with those args
        type_group = match.group(1)
        type_params = match.group(2)
        return generate_json_schema_helper(param, type_params, parent_group=type_group)
    elif "|" in param_type and "[" not in param_type:  # Convert Union shorthand to Union, recurse with that as input
        return generate_json_schema_helper(param, f"Union[{param_type.replace('|', ',')}]", parent_group=parent_group)
    else:  # Input is basic types, generate JSON Schema
        schemas = []
        param_types = [param_type]
        if parent_group in ["Union", "Optional"]:
            if "," in param_type:
                param_types = [p.strip() for p in param_type.split(",")]
        for p in param_types:
            subschema = {}
            if p == "str":
                subschema["type"] = "string"
                if "min_str_length" in param["loc_args"]:
                    subschema["minLength"] = param["loc_args"]["min_str_length"]
                if "max_str_length" in param["loc_args"]:
                    subschema["maxLength"] = param["loc_args"]["max_str_length"]
                if "json_schema" in param["loc_args"]:
                    # Without significant complexity, it is impossible to write a single regex to encompass
                    # the FPV blacklist, whitelist and pattern arguments, so only pattern is considered.
                    subschema["pattern"] = param["loc_args"]["json_schema"]
                if "whitelist" in param["loc_args"] or "blacklist" in param["loc_args"]:
                    warnings.warn("whitelist and blacklist cannot be translated to JSON Schema, please use pattern",
                                  Warning, stacklevel=2)
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
            elif p in ["StrEnum", "IntEnum"]:
                if p == "StrEnum":
                    subschema["type"] = "string"
                elif p == "IntEnum":
                    subschema["type"] = "integer"
                subschema["enum"] = param["enum_values"]
            else:
                warnings.warn(f"generate_json_schema_helper received an unexpected parameter type: {p}",
                              Warning, stacklevel=2)
            schemas.append(subschema)
        if len(schemas) == 1 and parent_group is None:
            return schemas[0]
        elif parent_group in ["Optional", "Union"]:
            return {"oneOf": schemas}
        elif parent_group in ["List", "list"]:
            schema = {"type": "array", "items": schemas[0]}
            if "min_list_length" in param["loc_args"]:
                schema["minItems"] = param["loc_args"]["min_list_length"]
            if "max_list_length" in param["loc_args"]:
                schema["maxItems"] = param["loc_args"]["max_list_length"]
            return schema
        else:
            warnings.warn(f"generate_json_schema_helper encountered an unexpected type: {param_type} with parent: "
                          f"{parent_group}", Warning, stacklevel=2)


def generate_json_schema_for_parameter(param):
    """ Generate JSON Schema for a single parameter """
    return generate_json_schema_helper(param, param["type"])


def generate_json_schema_for_parameters(params):
    """ Generate JSON Schema for all parameters of a route"""
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
    """ Generate OpenAPI Paths Object """
    oapi_paths = {}
    for route in get_route_docs():
        oapi_path_route = re.sub(r'<(\w+):(\w+)>', r'{\2}', route['rule'])
        oapi_path_route = re.sub(r'<(\w+)>', r'{\1}', oapi_path_route)
        oapi_path_item = {}
        oapi_operation = {}  # tags, summary, description, externalDocs, operationId, parameters, requestBody,
        # responses, callbacks, deprecated, security, servers
        oapi_parameters = []
        oapi_request_body = {"content": {}}
        if "MultiSource" in route["args"]:
            for arg in route["args"]["MultiSource"]:
                mod_arg = copy.deepcopy(arg)
                mod_arg["loc_args"].pop("sources")
                for source in arg["loc_args"]["sources"]:
                    source_name = source.__class__.__name__
                    if source_name in route["args"]:
                        route["args"][source_name].append(mod_arg)
                    else:
                        route["args"][source_name] = [mod_arg]
            route["args"].pop("MultiSource")
        for arg_loc in route["args"]:
            if arg_loc == "Form":
                oapi_request_body["content"]["application/x-www-form-urlencoded"] = {
                    "schema": generate_json_schema_for_parameters(route["args"][arg_loc])}
            elif arg_loc == "Json":
                oapi_request_body["content"]["application/json"] = {
                    "schema": generate_json_schema_for_parameters(route["args"][arg_loc])}
            elif arg_loc == "File":
                # https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#considerations-for-file-uploads
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
            else:
                warnings.warn(f"generate_openapi_paths_object encountered unexpected location: {arg_loc}",
                              Warning, stacklevel=2)
        if len(oapi_parameters) > 0:
            oapi_operation["parameters"] = oapi_parameters
        if len(oapi_request_body["content"].keys()) > 0:
            oapi_operation["requestBody"] = oapi_request_body
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
        return fpv_error(
            f"Flask-Parameter-Validation only supports OpenAPI {', '.join(supported_versions)}, "
            f"{openapi_base['openapi']} provided")
    if "paths" in openapi_base:
        return fpv_error(f"Flask-Parameter-Validation will overwrite the paths value of FPV_OPENAPI_BASE")
    openapi_paths = generate_openapi_paths_object()
    openapi_document = copy.deepcopy(openapi_base)
    openapi_document["paths"] = openapi_paths
    return jsonify(openapi_document)
