import functools
import inspect
import json
import re
import sys
import uuid
from typing import Any, Callable, Mapping, Optional, Union, get_args, get_origin, get_type_hints

from flask import current_app, request
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from .exceptions import InvalidParameterTypeError, MissingInputError, ValidationError
from .parameter_types import File, Form, Json, Parameter, Query, Route
from .parameter_types.multi_source import MultiSource

# TypedDict helpers (all in typing from 3.11)
if sys.version_info >= (3, 11):
    from typing import NotRequired, Required, is_typeddict
else:
    from typing_extensions import NotRequired, Required, is_typeddict

if sys.version_info >= (3, 10):
    from types import UnionType

    # Unions written as X | Y have their own type from 3.10 onwards
    UNION_TYPES = (Union, UnionType)
else:
    UNION_TYPES = (Union,)

# JSON media types (e.g. application/vnd.api+json)
JSON_CONTENT_TYPE = re.compile(r"application/[^+]*\+?json")

# Decorated view details by unique key
fn_list = {}


class _TypeConverter:
    """Raw input converter for type annotations"""

    def __init__(self, name: str, source: Parameter) -> None:
        """Store parameter name and source"""
        self.name = name
        self.source = source

    def _convert_union(self, user_input: Any, expected_type: Any) -> tuple[Any, bool]:
        """Convert to first matching union member"""
        # Optional[X] is also a Union, of X and None
        union_members = get_args(expected_type)
        for member_type in union_members:
            converted, member_matches = self.convert(user_input, member_type, union_members)
            if member_matches:
                return converted, True
        return user_input, False

    def _convert_list(self, user_input: Any, expected_type: Any) -> tuple[Any, bool]:
        """Convert input to typed list"""
        if type(user_input) is not list:
            # Accept Query and Form strings (JSON array or single value)
            if type(self.source) not in (Query, Form):
                return user_input, False
            user_input = self._decode_json_string(user_input)
            if type(user_input) is not list:
                user_input = [user_input]

        if user_input == [""]:
            # Treat blank value as empty list (e.g. ?value=)
            return [], True

        # Convert each item (Any for bare list)
        type_args = get_args(expected_type)
        item_type = type_args[0] if type_args else Any
        converted_list = []
        for item in user_input:
            converted, item_matches = self.convert(item, item_type)
            if not item_matches:
                return user_input, False
            converted_list.append(converted)
        return converted_list, True

    def _convert_typeddict(self, user_input: Any, expected_type: Any) -> tuple[Any, bool]:
        """Convert input to declared TypedDict"""
        # Decode and check required keys
        user_input = self._decode_json_string(user_input)
        if type(user_input) is not dict:
            return user_input, False
        if not all(key in user_input for key in expected_type.__required_keys__):
            return user_input, False

        # Convert each declared key
        type_hints = get_type_hints(expected_type)
        converted_dict = {}
        for key, item in user_input.items():
            if key not in type_hints:
                # Reject undeclared keys (declare optional keys as NotRequired)
                return user_input, False
            item_type = type_hints[key]

            # Unwrap Required and NotRequired (kept by get_type_hints before 3.11)
            if get_origin(item_type) in (Required, NotRequired):
                item_type = get_args(item_type)[0]
            converted, item_matches = self.convert(item, item_type)
            if not item_matches:
                return user_input, False
            converted_dict[key] = converted
        return converted_dict, True

    def _convert_dict(self, user_input: Any, expected_type: Any) -> tuple[Any, bool]:
        """Convert input to typed dict"""
        # Decode and check dict
        user_input = self._decode_json_string(user_input)
        if type(user_input) is not dict:
            return user_input, False

        # Convert keys and items (Any for bare dict)
        key_type, item_type = get_args(expected_type) or (Any, Any)
        converted_dict = {}
        for key, item in user_input.items():
            converted_key, key_matches = self.convert(key, key_type)
            converted_item, item_matches = self.convert(item, item_type)
            if not (key_matches and item_matches):
                return user_input, False
            converted_dict[converted_key] = converted_item
        return converted_dict, True

    def _convert_scalar(self, user_input: Any, expected_type: Any, union_members: tuple) -> tuple[Any, bool]:
        """Convert non-generic input via parameter source"""
        if expected_type is Any:
            return user_input, True

        # Convert with all union members (for blank_none on Optional[str])
        try:
            converted = self.source.convert(user_input, [expected_type, *union_members])
        except ValueError as error:
            raise ValidationError(str(error), self.name, expected_type)

        # Check exact type (rejects bool for int)
        return converted, type(converted) is expected_type

    @staticmethod
    def _decode_json_string(user_input: Any) -> Any:
        """Decode JSON string, else return input unchanged"""
        if type(user_input) is str and user_input:
            try:
                return json.loads(user_input)
            except ValueError:
                return user_input
        return user_input

    def convert(self, user_input: Any, expected_type: Any, union_members: tuple = ()) -> tuple[Any, bool]:
        """Convert input, return it and whether it matches"""
        origin = get_origin(expected_type)
        if origin in UNION_TYPES:
            return self._convert_union(user_input, expected_type)
        if expected_type is list or origin is list:
            return self._convert_list(user_input, expected_type)
        if is_typeddict(expected_type):
            return self._convert_typeddict(user_input, expected_type)
        if expected_type is dict or origin is dict:
            return self._convert_dict(user_input, expected_type)
        return self._convert_scalar(user_input, expected_type, union_members)


class ValidateParameters:
    """Validation decorator for Flask view inputs"""

    def __init__(
            self,
            error_handler: Optional[Callable[[Exception], Any]] = None,
            openapi_responses: Optional[dict] = None,
    ) -> None:
        """Store error handler and OpenAPI responses"""
        self.custom_error_handler = error_handler
        self.openapi_responses = openapi_responses

    def _register_for_docs(self, view_func: Callable) -> None:
        """Record view details in fn_list"""
        # Unique key (module and name can repeat)
        docs_key = f"{uuid.uuid4()}_{view_func.__module__}.{view_func.__name__}"

        # Store key on view (functools.wraps copies it to wrapper)
        view_func.__fpv_discriminated_sig__ = docs_key

        # Get decorator lines
        source_code = inspect.getsource(view_func)
        preamble = source_code[:source_code.find("def ")]
        decorators = [line for line in preamble.strip().splitlines() if line.strip().startswith("@")]

        # Store view details
        fn_list[docs_key] = {
            "argspec": inspect.getfullargspec(view_func),
            "docstring": view_func.__doc__.strip() if view_func.__doc__ else None,
            "decorators": decorators,
            "openapi_responses": self.openapi_responses,
        }

    def _validate_request(self, view_func: Callable, route_kwargs: dict) -> tuple[Optional[dict], Any]:
        """Validate request, return view inputs or error response"""
        expected_inputs = inspect.signature(view_func).parameters

        # Parse JSON body
        try:
            json_input = self._get_json_body()
        except BadRequest:
            return None, ({"error": "Could not parse JSON."}, 400)

        # Collect inputs by source
        split_csv = self._query_csv_split_settings(expected_inputs)
        request_inputs = {
            Route: route_kwargs,
            Json: json_input or {},
            Query: self._flatten_multidict(request.args, split_csv),
            Form: self._flatten_multidict(request.form),
            File: self._flatten_multidict(request.files),
        }

        # Validate each parameter
        validated_inputs = {}
        for expected_input in expected_inputs.values():
            try:
                validated_inputs[expected_input.name] = self.validate(expected_input, request_inputs)
            except Exception as error:
                if self.custom_error_handler is not None:
                    return None, self.custom_error_handler(error)
                if isinstance(error, (MissingInputError, ValidationError)):
                    return None, ({"error": str(error)}, 400)
                raise
        return validated_inputs, None

    @staticmethod
    def _get_json_body() -> Any:
        """Return parsed body if content type is JSON"""
        content_type = request.headers.get("Content-Type")
        if content_type is not None and JSON_CONTENT_TYPE.search(content_type):
            return request.json
        return None

    @staticmethod
    def _query_csv_split_settings(expected_inputs: Mapping[str, inspect.Parameter]) -> dict[str, bool]:
        """Map input names to Query CSV split flags"""
        is_csv_disabled_by_default = current_app.config.get("FPV_LIST_DISABLE_QUERY_CSV", False)
        split_csv = {}
        for name, expected_input in expected_inputs.items():
            parameter = expected_input.default
            is_csv_disabled = parameter.list_disable_query_csv
            if is_csv_disabled is None:
                is_csv_disabled = is_csv_disabled_by_default
            split_csv[parameter.alias or name] = not is_csv_disabled
        return split_csv

    @staticmethod
    def _flatten_multidict(request_fields: MultiDict, split_csv: Optional[dict[str, bool]] = None) -> dict:
        """Flatten MultiDict to dict, lists for repeated keys"""
        split_csv = split_csv or {}
        flattened = {}
        for key, values in request_fields.lists():
            # Split on commas where enabled
            if split_csv.get(key):
                values = [part for value in values for part in value.split(",")]
            flattened[key] = values[0] if len(values) == 1 else values
        return flattened

    @staticmethod
    def _is_optional(annotation: Any) -> bool:
        """Check if annotation allows None"""
        return type(None) in getattr(annotation, "__args__", ())

    def __call__(self, view_func: Callable) -> Callable:
        """Register view and wrap with validation"""
        self._register_for_docs(view_func)

        # Pick async or sync wrapper
        if inspect.iscoroutinefunction(view_func):
            @functools.wraps(view_func)
            async def wrapper(**route_kwargs: Any) -> Any:
                """Validate request then await view"""
                inputs, error_response = self._validate_request(view_func, route_kwargs)
                if inputs is None:
                    return error_response
                return await view_func(**inputs)
        else:
            @functools.wraps(view_func)
            def wrapper(**route_kwargs: Any) -> Any:
                """Validate request then call view"""
                inputs, error_response = self._validate_request(view_func, route_kwargs)
                if inputs is None:
                    return error_response
                return view_func(**inputs)

        return wrapper

    def validate(self, expected_input: inspect.Parameter, all_request_inputs: dict) -> Any:
        """Find, convert and validate one view argument"""
        expected_type = expected_input.annotation
        parameter = expected_input.default  # e.g. Query(), Json() or MultiSource(...)
        name = parameter.alias or expected_input.name
        sources = parameter.sources if type(parameter) is MultiSource else [parameter]

        # Use first source with input or default
        for index, source in enumerate(sources):
            # Reject unknown source types
            if type(source) not in all_request_inputs:
                raise InvalidParameterTypeError(source)

            # Get input or default
            user_input = all_request_inputs[type(source)].get(name)
            if user_input is None:
                user_input = source.default

            # Handle missing input
            if user_input is None:
                if index < len(sources) - 1:
                    continue
                if self._is_optional(expected_type):
                    return None
                raise MissingInputError(name, type(source))

            # Convert to expected type
            converted_input, type_matches = _TypeConverter(name, source).convert(user_input, expected_type)

            # Check constraints before type (their errors take precedence)
            try:
                source.validate(converted_input)
            except ValueError as error:
                raise ValidationError(str(error), name, expected_type)

            # Reject type mismatch
            if not type_matches:
                raise ValidationError(f"must be type '{expected_type}'", name, expected_type)
            return converted_input

    @classmethod
    def get_fn_list(cls) -> dict:
        """Return details of decorated views"""
        return fn_list
