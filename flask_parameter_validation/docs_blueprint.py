"""Docs blueprint and OpenAPI generation for validated routes"""
import datetime
import inspect
import json
import re
import sys
import uuid
import warnings
from copy import deepcopy
from dataclasses import dataclass, replace
from enum import Enum, EnumMeta
from typing import Annotated, Any, Callable, Optional, Union

from flask import Blueprint, Response, current_app, jsonify, render_template

from .exceptions.exceptions import ConfigurationError
from .parameter_validation import ValidateParameters

# TypedDict check (typing_extensions has its own TypedDict before 3.11)
if sys.version_info >= (3, 11):
    from typing import is_typeddict
else:
    from typing_extensions import is_typeddict

# Unions written as X | Y (3.10 onwards)
if sys.version_info >= (3, 10):
    from types import UnionType

# PEP 702 deprecated decorator (in warnings from 3.13)
if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

# Legacy docs routes deprecation message
LEGACY_ROUTE_DEPRECATION = "Use /openapi instead"

# Bootstrap badge class per HTTP method
HTTP_METHOD_BADGES = {"GET": "bg-primary", "POST": "bg-success", "DELETE": "bg-danger"}

# Supported OpenAPI versions
SUPPORTED_OPENAPI_VERSIONS = ("3.1.0", "3.1.1", "3.1.2", "3.2.0")

# Union type names containing None (e.g. Union[int, NoneType])
OPTIONAL_UNION_NAME = re.compile(r"Union\[.*None.*")

# Generic type names (e.g. List[int], group 1 is List)
GENERIC_TYPE_NAME = re.compile(r"(\w+)\[([\w\[\] ,.]+)]")

# Annotated hint class (no __name__ on 3.9)
ANNOTATED_ALIAS = type(Annotated[int, ""])

# Warning stack levels (point at generate_json_schema_helper caller)
SCHEMA_STACKLEVEL = 2
TYPE_SCHEMA_STACKLEVEL = 3

# JSON Schema keywords per Parameter constraint
STRING_CONSTRAINTS = {"min_str_length": "minLength", "max_str_length": "maxLength", "pattern": "pattern"}
INTEGER_CONSTRAINTS = {"min_int": "minimum", "max_int": "maximum"}
LIST_CONSTRAINTS = {"min_list_length": "minItems", "max_list_length": "maxItems"}

# Flask rule variables (e.g. <int:id> and <id>)
TYPED_RULE_VARIABLE = re.compile(r"<(\w+):(\w+)>")
RULE_VARIABLE = re.compile(r"<(\w+)>")

# Request body media types per source
BODY_MEDIA_TYPES = {"Form": "application/x-www-form-urlencoded", "Json": "application/json"}

# File media type without content_types
DEFAULT_FILE_MEDIA_TYPE = "application/octet-stream"

# Decorators marking route deprecated (PEP 702)
DEPRECATED_DECORATORS = ("@warnings.deprecated", "@deprecated")

# Methods left out of OpenAPI (Flask adds them automatically)
IGNORED_METHODS = ("OPTIONS", "HEAD")

# Docs routes under /docs
docs_blueprint = Blueprint("docs", __name__, url_prefix="/docs", template_folder="./templates")


@dataclass
class ArgumentDetails:
    """Docs for one view argument"""

    name: str
    type_name: str  # Type hint as string (e.g. List[int])
    location: str  # Parameter class name (e.g. Query)
    location_args: dict  # Formatted non-None Parameter arguments
    raw_type: Any  # Annotation from view signature

    @property
    def request_name(self) -> str:
        """Get alias, else argument name"""
        return self.location_args.get("alias", self.name)

    def to_dict(self, include_raw_type: bool = False) -> dict:
        """Convert to legacy docs format"""
        # Use legacy keys
        legacy_docs = {"name": self.name, "type": self.type_name, "loc": self.location, "loc_args": self.location_args}

        # Add raw type if requested (not JSON serialisable)
        if include_raw_type:
            legacy_docs["raw_type"] = self.raw_type
        return legacy_docs


def _type_base_name(type_hint: Any) -> str:
    """Get type hint name without arguments"""
    # Name X | Y unions (all unions from 3.14)
    if sys.version_info >= (3, 10) and isinstance(type_hint, UnionType):
        return "Union"

    # Use __name__ on classes, and typing generics from 3.10
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__

    # Use _name on typing generics on 3.9 (e.g. List[int])
    if hasattr(type_hint, "_name") and type_hint._name is not None:
        return type_hint._name

    # Use origin name for Optional and Union on 3.9
    return type_hint.__origin__._name


def _format_parameter_argument(name: str, value: Any) -> Any:
    """Format Parameter argument for docs"""
    # Name functions and classes by module path
    if callable(value):
        return f"{value.__module__}.{value.__name__}"

    # Format str and int Enum members
    if issubclass(type(value), Enum):
        member_name = f"{type(value).__name__}.{value.name}"
        if issubclass(type(value), int):
            return f"{member_name}: {value.value}"
        if issubclass(type(value), str):
            return f"{member_name}: '{value.value}'"
        return "FPV: Unsupported Enum type"

    # Convert times to ISO 8601
    if type(value).__name__ == "time":
        return value.isoformat()

    # Name MultiSource sources by class
    if name == "sources":
        return [type(source).__name__ for source in value]

    # Keep other values
    return value


def _get_parameter_schema(param: ArgumentDetails) -> dict:
    """Get json_schema argument, else generated schema"""
    if "json_schema" in param.location_args:
        return param.location_args["json_schema"]
    return generate_json_schema_for_parameter(param)


def _add_schema_constraints(schema: dict, param: Optional[ArgumentDetails], constraint_keywords: dict) -> None:
    """Copy Parameter constraints to schema keywords"""
    # Skip if no Parameter
    if param is None:
        return

    # Copy given constraints
    for constraint, keyword in constraint_keywords.items():
        if constraint in param.location_args:
            schema[keyword] = param.location_args[constraint]


def _typeddict_schema(type_name: str, raw_type: type) -> dict:
    """Generate JSON Schema for TypedDict"""
    # Read source for field comments (none for functional TypedDict)
    try:
        source_code = inspect.getsource(raw_type)
    except OSError:
        source_code = ""

    # Collect field schemas and required keys
    properties = {}
    required_keys = []
    for key, field_type in raw_type.__annotations__.items():
        # Generate field schema
        field_type_name = recursively_resolve_type_hint(field_type)
        properties[key] = generate_json_schema_helper(None, field_type)

        # Use trailing field comment as description (e.g. x: int  # X coordinate)
        field_comments = re.findall(rf"^\s*{key}\s*:\s*{field_type_name}\s*#\s*(.*)$", source_code, flags=re.MULTILINE)
        if field_comments:
            properties[key]["description"] = field_comments[0]

        # Require key unless NotRequired (total=False keys need Required)
        is_required_key = "NotRequired[" not in field_type_name and (
            raw_type.__total__ or "Required[" in field_type_name)
        if is_required_key:
            required_keys.append(key)

    # Build object schema
    schema = {"type": "object", "properties": properties}
    if required_keys:
        schema["required"] = required_keys
    schema["title"] = type_name

    # Use docstring as description (skip one inherited from dict)
    type_description = inspect.getdoc(raw_type)
    if type_description and type_description != inspect.getdoc(dict):
        schema["description"] = type_description
    return schema


def _enum_schema(type_name: str, raw_type: EnumMeta) -> dict:
    """Generate JSON Schema for Enum"""
    # Set type from str or int mixin
    schema = {}
    if issubclass(raw_type, str):
        schema["type"] = "string"
    elif issubclass(raw_type, int):
        schema["type"] = "integer"
    else:
        warnings.warn(f"Unsupported enum type: {type_name}", Warning, stacklevel=TYPE_SCHEMA_STACKLEVEL)

    # Read source for member comments (raises for functional Enums)
    source_code = inspect.getsource(raw_type)

    # Add member options
    options = []
    for member in raw_type:
        option_schema = {"title": member.name, "const": member.value}

        # Use trailing member comment as description (e.g. RED = "red"  # Red)
        member_comments = re.findall(rf"^\s*{member.name}\s*=\s*['\"]?{member.value}['\"]?\s*#\s*(.*)$", source_code,
                                     flags=re.MULTILINE)
        if member_comments:
            option_schema["description"] = member_comments[0]
        options.append(option_schema)
    schema["oneOf"] = options

    # Use docstring as description (skip one inherited from str or int)
    type_description = inspect.getdoc(raw_type)
    if type_description and type_description not in [inspect.getdoc(str), inspect.getdoc(int)]:
        schema["description"] = type_description

    # Set title to type name
    schema["title"] = type_name
    return schema


def _generic_schema(param: Optional[ArgumentDetails], type_name: str, raw_type: Any, generic_name: str) -> dict:
    """Generate JSON Schema for generic type"""
    # Build array schema (str and int constraints apply per item)
    if generic_name in ("List", "list"):
        item_type_schemas = [generate_json_schema_helper(param, item_type) for item_type in raw_type.__args__]

        # Use oneOf for several item types
        items_schema = item_type_schemas[0] if len(item_type_schemas) == 1 else {"oneOf": item_type_schemas}
        schema = {"type": "array", "items": items_schema}

        # Add list length constraints
        _add_schema_constraints(schema, param, LIST_CONSTRAINTS)
        return schema

    # Build oneOf from union members
    if generic_name in ("Optional", "Union"):
        return {"oneOf": [generate_json_schema_helper(None, member_type) for member_type in raw_type.__args__]}

    # Unwrap Required and NotRequired
    if generic_name in ("Required", "NotRequired"):
        return generate_json_schema_helper(param, raw_type.__args__[0])

    # Use dict value type for additionalProperties
    if generic_name == "dict":
        value_schema = generate_json_schema_helper(None, raw_type.__args__[1])
        return {"type": "object", "additionalProperties": value_schema}

    # Unwrap Annotated
    if generic_name == "Annotated" or type(raw_type) is ANNOTATED_ALIAS:
        schema = generate_json_schema_helper(param, raw_type.__origin__)

        # Use first str metadata as description
        for annotation in raw_type.__metadata__:
            if type(annotation) is str:
                schema["description"] = annotation
                break
        return schema

    # Warn on other generics (e.g. tuple[int, str])
    warnings.warn(f"Unsupported generic type {type_name}", Warning, stacklevel=TYPE_SCHEMA_STACKLEVEL)
    return {}


def _flatten_multisource_args(route_args: dict[str, list[ArgumentDetails]]) -> None:
    """Move MultiSource args to their sources"""
    # Skip routes without MultiSource args
    if "MultiSource" not in route_args:
        return

    for arg in route_args["MultiSource"]:
        # Remove sources from location_args
        sources = arg.location_args.pop("sources")

        # Copy arg to each source
        for source in sources:
            route_args.setdefault(source, []).append(replace(deepcopy(arg), location=source))

    # Remove MultiSource args
    del route_args["MultiSource"]


def _collect_openapi_inputs(route_args: dict[str, list[ArgumentDetails]], path: str) -> tuple[str, list, dict]:
    """Return aliased path, parameters and body"""
    parameters = []
    body_content = {}
    for location, args_at_location in route_args.items():
        if location in BODY_MEDIA_TYPES:
            # Add Form and Json schemas
            body_content[BODY_MEDIA_TYPES[location]] = {
                "schema": generate_json_schema_for_parameters(args_at_location)}
        elif location == "File":
            # Add File media types (OpenAPI 3.1 file upload guidance)
            for arg in args_at_location:
                for media_type in arg.location_args.get("content_types", [DEFAULT_FILE_MEDIA_TYPE]):
                    body_content[media_type] = {}
        elif location in ("Route", "Query"):
            for arg in args_at_location:
                # Rename path parameter to alias
                request_name = arg.request_name
                if "alias" in arg.location_args:
                    path = path.replace(f"{{{arg.name}}}", f"{{{request_name}}}")

                # Skip Route args not in path (views can serve several routes)
                is_path_parameter = location == "Route"
                if is_path_parameter and f"{{{request_name}}}" not in path:
                    continue

                # Add path or query parameter
                parameters.append({
                    "name": request_name,
                    "in": "path" if is_path_parameter else "query",
                    "required": True if is_path_parameter else parameter_required(arg),
                    "schema": _get_parameter_schema(arg),
                })
    return path, parameters, body_content


def _build_openapi_operation(route: dict, parameters: list, body_content: dict) -> dict:
    """Build OpenAPI operation for route"""
    # Add parameters and request body if any
    operation = {}
    if parameters:
        operation["parameters"] = parameters
    if body_content:
        operation["requestBody"] = {"content": body_content}

    # Mark deprecated views
    for decorator in route["decorators"]:
        if any(marker in decorator for marker in DEPRECATED_DECORATORS):
            operation["deprecated"] = True

    # Add responses and docstring if given
    if route["responses"]:
        operation["responses"] = route["responses"]
    if route["docstring"]:
        operation["description"] = route["docstring"]
    return operation


def _collect_route_docs() -> list[dict]:
    """Get docs for every validated route"""
    route_docs = []
    for rule in current_app.url_map.iter_rules():
        # Skip views without ValidateParameters
        view_docs = get_function_docs(current_app.view_functions[rule.endpoint])
        if not view_docs:
            continue

        # Add rule and methods
        view_docs["rule"] = str(rule)
        view_docs["methods"] = [str(method) for method in rule.methods]
        route_docs.append(view_docs)
    return route_docs


def _get_legacy_docs() -> dict:
    """Get legacy docs and page settings"""
    # Read docs page config (README lists defaults)
    config = current_app.config
    return {
        "site_name": config.get("FPV_DOCS_SITE_NAME", "Site"),
        "docs": get_route_docs(),
        "custom_blocks": config.get("FPV_DOCS_CUSTOM_BLOCKS", []),
        "default_theme": config.get("FPV_DOCS_DEFAULT_THEME", "light"),
    }


def get_function_docs(func: Callable) -> Optional[dict]:
    """Get view docs, None without ValidateParameters"""
    # Find details recorded by ValidateParameters
    docs_key = getattr(func, "__fpv_discriminated_sig__", None)
    fdocs = ValidateParameters.get_fn_list().get(docs_key)
    if fdocs is None:
        return None

    # Build view docs
    return {
        "docstring": format_docstring(fdocs["docstring"]),
        "decorators": fdocs["decorators"],
        "args": extract_argument_details(fdocs),
        "responses": fdocs["openapi_responses"],
    }


def format_docstring(docstring: Optional[str]) -> Optional[str]:
    """Format docstring as HTML"""
    # Skip empty docstring
    if not docstring:
        return None

    # Convert newlines and four-space indents to HTML
    html_docstring = docstring.strip().replace("\n", "<br/>")
    return html_docstring.replace("    ", "&nbsp;" * 4)


def extract_argument_details(fdocs: dict) -> dict[str, list[ArgumentDetails]]:
    """Group argument details by location"""
    args_by_location = {}
    for index, arg_name in enumerate(fdocs["argspec"].args):
        # Build argument details
        type_name, raw_type = get_arg_type_hint(fdocs, arg_name)
        arg_details = ArgumentDetails(
            name=arg_name,
            type_name=type_name,
            location=get_arg_location(fdocs, index),
            location_args=get_arg_location_details(fdocs, index),
            raw_type=raw_type,
        )

        # Group by location
        args_by_location.setdefault(arg_details.location, []).append(arg_details)
    return args_by_location


def recursively_resolve_type_hint(type_to_resolve: Any) -> str:
    """Convert type hint to string"""
    # Return name if no arguments
    type_name = _type_base_name(type_to_resolve)
    if not hasattr(type_to_resolve, "__args__"):
        return type_name

    # Add generic arguments
    resolved_args = ", ".join([recursively_resolve_type_hint(arg) for arg in type_to_resolve.__args__])
    return f"{type_name}[{resolved_args}]"


def get_arg_type_hint(fdocs: dict, arg_name: str) -> tuple[str, Any]:
    """Get type name and raw type"""
    arg_type = fdocs["argspec"].annotations[arg_name]
    return recursively_resolve_type_hint(arg_type), arg_type


def get_arg_location(fdocs: dict, idx: int) -> str:
    """Get Parameter class name (e.g. Query)"""
    return type(fdocs["argspec"].defaults[idx]).__name__


def get_arg_location_details(fdocs: dict, idx: int) -> dict:
    """Format non-None Parameter arguments"""
    parameter = fdocs["argspec"].defaults[idx]
    return {
        name: _format_parameter_argument(name, value)
        for name, value in parameter.__dict__.items()
        if value is not None
    }


def fpv_error(message: str) -> Response:
    """Return JSON error response"""
    return jsonify({"error": message})


def parameter_required(param: ArgumentDetails) -> bool:
    """Check if parameter is required"""
    # Allow missing Optional types
    if param.type_name.startswith("Optional[") or OPTIONAL_UNION_NAME.match(param.type_name):
        return False

    # Require if no default
    return "default" not in param.location_args


# No Parameter for union members, dict values and TypedDict fields
def generate_json_schema_helper(param: Optional[ArgumentDetails], raw_type: Any) -> dict:
    """Generate JSON Schema for type hint"""
    # Name type hint (e.g. List[int])
    type_name = recursively_resolve_type_hint(raw_type)

    # Build schema by type
    if raw_type is str:
        schema = {"type": "string"}
        _add_schema_constraints(schema, param, STRING_CONSTRAINTS)
    elif raw_type is int:
        schema = {"type": "integer"}
        _add_schema_constraints(schema, param, INTEGER_CONSTRAINTS)
    elif raw_type is bool:
        schema = {"type": "boolean"}
    elif raw_type is float:
        schema = {"type": "number"}
    elif raw_type is datetime.datetime:
        # Warn on datetime_format (JSON Schema has ISO 8601 only)
        schema = {"type": "string", "format": "date-time"}
        if param is not None and "datetime_format" in param.location_args:
            warnings.warn("datetime_format cannot be translated to JSON Schema, please use ISO8601 date-time",
                          Warning, stacklevel=SCHEMA_STACKLEVEL)
    elif raw_type is datetime.date:
        schema = {"type": "string", "format": "date"}
    elif raw_type is datetime.time:
        schema = {"type": "string", "format": "time"}
    elif raw_type is type(None):
        schema = {"type": "null"}
    elif is_typeddict(raw_type):
        schema = _typeddict_schema(type_name, raw_type)
    elif raw_type is dict:
        schema = {"type": "object"}
    elif type(raw_type) is EnumMeta:
        schema = _enum_schema(type_name, raw_type)
    elif raw_type is uuid.UUID:
        schema = {"type": "string", "format": "uuid"}
    else:
        # Warn on other non-generic types
        generic_match = GENERIC_TYPE_NAME.match(type_name)
        if not generic_match:
            warnings.warn(f"Unsupported type {type_name}", Warning, stacklevel=SCHEMA_STACKLEVEL)
            return {}

        # Build schema for generic types (e.g. list[int])
        schema = _generic_schema(param, type_name, raw_type, generic_match.group(1))

    # Add comment and default from Parameter
    if param:
        if "comment" in param.location_args:
            schema["description"] = param.location_args["comment"]
        if "default" in param.location_args:
            schema["default"] = param.location_args["default"]
    return schema


def generate_json_schema_for_parameter(param: ArgumentDetails) -> dict:
    """Generate JSON Schema for one parameter"""
    return generate_json_schema_helper(param, param.raw_type)


def generate_json_schema_for_parameters(params: list[ArgumentDetails]) -> dict:
    """Generate object JSON Schema for parameters"""
    # Collect properties and required names
    properties = {}
    required_names = []
    for param in params:
        request_name = param.request_name
        properties[request_name] = _get_parameter_schema(param)
        if parameter_required(param):
            required_names.append(request_name)

    # Build object schema
    schema = {"type": "object", "properties": properties}
    if required_names:
        schema["required"] = required_names
    return schema


def get_route_docs(include_raw_type: bool = False) -> list[dict]:
    """Get docs for every validated route"""
    route_docs = _collect_route_docs()

    # Convert args to legacy format
    for view_docs in route_docs:
        view_docs["args"] = {
            location: [arg.to_dict(include_raw_type) for arg in args_at_location]
            for location, args_at_location in view_docs["args"].items()
        }
    return route_docs


def generate_openapi_paths_object() -> dict:
    """Generate OpenAPI paths for validated routes"""
    openapi_paths = {}
    for route in _collect_route_docs():
        # Convert rule variables to path parameters (e.g. <int:id> to {id})
        path = TYPED_RULE_VARIABLE.sub(r"{\2}", route["rule"])
        path = RULE_VARIABLE.sub(r"{\1}", path)

        # Split MultiSource args by source
        _flatten_multisource_args(route["args"])

        # Collect parameters and request body
        path, parameters, body_content = _collect_openapi_inputs(route["args"], path)

        # Share operation across route methods
        operation = _build_openapi_operation(route, parameters, body_content)
        path_item = {method.lower(): operation for method in route["methods"] if method not in IGNORED_METHODS}

        # Merge with other rules on same path
        openapi_paths[path] = openapi_paths.get(path, {}) | path_item
    return openapi_paths


def generate_openapi_docs() -> Union[dict, Response]:
    """Generate OpenAPI document, raises if disabled"""
    # Require FPV_OPENAPI_ENABLE
    config = current_app.config
    if not config.get("FPV_OPENAPI_ENABLE", False):
        raise ConfigurationError("FPV_OPENAPI_ENABLE is not set, and defaults to False")

    # Check FPV_OPENAPI_BASE (unset fails version check)
    openapi_base = config.get("FPV_OPENAPI_BASE", {"openapi": None})
    if openapi_base["openapi"] not in SUPPORTED_OPENAPI_VERSIONS:
        return fpv_error(f"Flask-Parameter-Validation only supports OpenAPI {', '.join(SUPPORTED_OPENAPI_VERSIONS)}, "
                         f"provided: {openapi_base['openapi']}")
    if "paths" in openapi_base:
        return fpv_error("Flask-Parameter-Validation will overwrite the paths value of FPV_OPENAPI_BASE")

    # Add paths to deep copy of FPV_OPENAPI_BASE
    openapi_paths = generate_openapi_paths_object()
    openapi_document = json.loads(json.dumps(openapi_base))
    openapi_document["paths"] = openapi_paths
    return openapi_document


@docs_blueprint.app_template_filter()
def http_badge_bg(http_method: str) -> str:
    """Get badge class for HTTP method"""
    # Use warning badge for other methods
    return HTTP_METHOD_BADGES.get(http_method, "bg-warning")


@docs_blueprint.route("/")
@deprecated(LEGACY_ROUTE_DEPRECATION)
def docs_html() -> str:
    """Render docs as HTML page"""
    return render_template("fpv_default_docs.html", **_get_legacy_docs())


@docs_blueprint.route("/json")
@deprecated(LEGACY_ROUTE_DEPRECATION)
def docs_json() -> Response:
    """Return docs as JSON"""
    return jsonify(_get_legacy_docs())


@docs_blueprint.route("/openapi")
def docs_openapi() -> Response:
    """Return OpenAPI document as JSON"""
    return jsonify(generate_openapi_docs())
