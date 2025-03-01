from enum import Enum
import flask
from flask import Blueprint, current_app, jsonify

from flask_parameter_validation import ValidateParameters

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
        if hasattr(type_to_resolve, "__args__"):
            return (
                f"{type_to_resolve.__name__}[{', '.join([recursively_resolve_type_hint(a) for a in type_to_resolve.__args__])}]"
            )
        return type_to_resolve.__name__
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
