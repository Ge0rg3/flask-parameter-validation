import asyncio
import functools
import inspect
import re
import uuid
from inspect import signature
from typing import Optional

import flask
from flask import request, Response
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequest
from .exceptions import (InvalidParameterTypeError, MissingInputError,
                         ValidationError)
from .parameter_types import File, Form, Json, Query, Route
from .parameter_types.multi_source import MultiSource

fn_list = dict()

list_type_hints = ["typing.List", "typing.Optional[typing.List", "list", "typing.Optional[list"]

class ValidateParameters:
    @classmethod
    def get_fn_list(cls):
        return fn_list

    def __init__(self, error_handler=None):
        self.custom_error_handler = error_handler

    def __call__(self, f):
        """
        Parent flow for validating each required parameter
        """
        fsig = f.__module__ + "." + f.__name__
        # Add a discriminator to the function signature, store it in the properties of the function
        # This is used in documentation generation to associate the info gathered from inspecting the
        # function with the properties passed to the ValidateParameters decorator
        f.__fpv_discriminated_sig__ = f"{uuid.uuid4()}_{fsig}"
        fsig = f.__fpv_discriminated_sig__
        argspec = inspect.getfullargspec(f)
        source = inspect.getsource(f)
        index = source.find("def ")
        decorators = []
        for line in source[:index].strip().splitlines():
            if line.strip()[0] == "@":
                decorators.append(line)
        fdocs = {
            "argspec": argspec,
            "docstring": f.__doc__.strip() if f.__doc__ else None,
            "decorators": decorators.copy(),
        }
        fn_list[fsig] = fdocs

        def nested_func_helper(**kwargs):
            """
            Validates the inputs of a Flask route or returns an error. Returns
            are wrapped in a dictionary with a flag to let nested_func() know
            if it should unpack the resulting dictionary of inputs as kwargs,
            or just return the error message.
            """
            # Step 1 - Get expected input details as dict
            expected_inputs = signature(f).parameters

            # Step 2 - Validate JSON inputs
            json_input = None
            if request.headers.get("Content-Type") is not None:
                if re.search(
                        "application/[^+]*[+]?(json);?", request.headers.get("Content-Type")
                ):
                    try:
                        json_input = request.json
                    except BadRequest:
                        return {"error": ({"error": "Could not parse JSON."}, 400), "validated": False}

            # Step 3 - Extract list of parameters expected to be lists (otherwise all values are converted to lists), and for Query params, whether they should split strings by `,`
            expected_list_params = {}
            default_list_disable_query_csv = flask.current_app.config.get("FPV_LIST_DISABLE_QUERY_CSV", False)
            for name, param in expected_inputs.items():
                if any([str(param.annotation).startswith(list_hint) for list_hint in list_type_hints]):
                    list_disable_query_csv = default_list_disable_query_csv
                    if param.default.list_disable_query_csv is not None:
                        list_disable_query_csv = param.default.list_disable_query_csv
                    expected_list_params[param.default.alias or name] = not list_disable_query_csv

            # Step 4 - Convert request inputs to dicts
            request_inputs = {
                Route: kwargs.copy(),
                Json: json_input or {},
                Query: self._to_dict_with_lists(request.args, list(expected_list_params.keys()), list(expected_list_params.values())),
                Form: self._to_dict_with_lists(request.form, list(expected_list_params.keys())),
                File: self._to_dict_with_lists(request.files, list(expected_list_params.keys())),
            }

            # Step 5 - Validate each expected input
            validated_inputs = {}
            for expected in expected_inputs.values():
                if self.custom_error_handler is None:
                    try:
                        new_input = self.validate(expected, request_inputs)
                    except (MissingInputError, ValidationError) as e:
                        return {"error": ({"error": str(e)}, 400), "validated": False}
                else:
                    try:
                        new_input = self.validate(expected, request_inputs)
                    except Exception as e:
                        return {"error": self.custom_error_handler(e), "validated": False}
                validated_inputs[expected.name] = new_input

            return {"inputs": validated_inputs, "validated": True}

        if asyncio.iscoroutinefunction(f):
            # If the view function is async, return and await a coroutine
            @functools.wraps(f)
            async def nested_func(**kwargs):
                validated_inputs = nested_func_helper(**kwargs)
                if validated_inputs["validated"]:
                    return await f(**validated_inputs["inputs"])
                return validated_inputs["error"]
        else:
            # If the view function is not async, return a function
            @functools.wraps(f)
            def nested_func(**kwargs):
                validated_inputs = nested_func_helper(**kwargs)
                if validated_inputs["validated"]:
                    return f(**validated_inputs["inputs"])
                return validated_inputs["error"]

        nested_func.__name__ = f.__name__
        return nested_func

    def _to_dict_with_lists(
            self, multi_dict: ImmutableMultiDict, expected_lists: list[str], split_strings: Optional[list[bool]] = None
    ) -> dict:
        dict_with_lists = {}
        for key, values in multi_dict.lists():
            # Only create lists for keys that are expected to be lists
            if key in expected_lists:
                key_index = expected_lists.index(key)
                list_values = []
                for value in values:
                    if value != "" or len(values) > 1:
                        if split_strings and split_strings[key_index]:
                            list_values.extend(value.split(","))
                        else:
                            list_values.append(value)
                dict_with_lists[key] = list_values
            else:
                # If only one value and not expected to be a list, don't use a list
                dict_with_lists[key] = values[0] if len(values) == 1 else values
        return dict_with_lists

    def _generic_types_validation_helper(self, expected_name, expected_input_type, expected_input_type_str, user_input, source):
        """
        Perform recursive validation of generic types (Optional, Union, and List/list)
        """
        # In python3.7+, typing.Optional is used instead of typing.Union[..., None]
        if expected_input_type_str.startswith("typing.Optional"):
            sub_expected_input_types = expected_input_type
            sub_expected_input_type_str = expected_input_type_str.replace("typing.Optional[", "typing.Union[None, ")
            user_inputs, sub_expected_input_types = self._generic_types_validation_helper(expected_name, sub_expected_input_types, sub_expected_input_type_str, user_input, source)
        elif expected_input_type_str.startswith("typing.Union"):
            if type(expected_input_type) is tuple or type(expected_input_type) is list:
                sub_expected_input_types = expected_input_type
            else:
                sub_expected_input_types = expected_input_type.__args__
            sub_expected_input_type_str = expected_input_type_str[expected_input_type_str.index("[") + 1:-1]
            if type(user_input) is list:
                user_inputs = user_input
            else:
                user_inputs = [user_input]
            user_inputs, sub_expected_input_types = self._generic_types_validation_helper(expected_name, sub_expected_input_types, sub_expected_input_type_str, user_inputs, source)
            # If typing.List in optional and user supplied valid list, convert remaining check only for list
            for exp_type in sub_expected_input_types:
                if any(str(exp_type).startswith(list_hint) for list_hint in list_type_hints):
                    if type(user_input) is list:
                        if hasattr(exp_type, "__args__"):
                            sub_expected_input_types = exp_type.__args__
                            if len(sub_expected_input_types) == 1:
                                sub_expected_input_types = sub_expected_input_types[0]
                            sub_expected_input_type_str = str(sub_expected_input_types)
                            user_inputs = user_input
                            user_inputs, sub_expected_input_types = self._generic_types_validation_helper(expected_name, sub_expected_input_types, sub_expected_input_type_str, user_inputs, source)
        # If list, expand inner typing items. Otherwise, convert to list to match anyway.
        elif any(expected_input_type_str.startswith(list_hint) for list_hint in list_type_hints):
            if hasattr(expected_input_type, "__args__"):
                sub_expected_input_types = expected_input_type.__args__[0]
            else:
                sub_expected_input_types = expected_input_type
            sub_expected_input_type_str = expected_input_type_str[expected_input_type_str.index("[")+1:-1]
            if type(user_input) is list:
                user_inputs = user_input
            else:
                user_inputs = [user_input]
            user_inputs, sub_expected_input_types = self._generic_types_validation_helper(expected_name, sub_expected_input_types, sub_expected_input_type_str, user_inputs, source)
        else:
            if type(user_input) is list:
                user_inputs = user_input
            else:
                user_inputs = [user_input]
            if type(expected_input_type) is list or type(expected_input_type) is tuple:
                sub_expected_input_types = expected_input_type
            elif type(expected_input_type) is list and len(expected_input_type) > 0 and hasattr(expected_input_type[0], "__len__"):
                sub_expected_input_types = expected_input_type[0]
            elif expected_input_type is list and not hasattr(expected_input_type, "__args__"):
                return [user_inputs], [expected_input_type]
            else:
                sub_expected_input_types = [expected_input_type]
            for count, value in enumerate(user_inputs):
                try:
                    user_inputs[count] = source.convert(
                        value, sub_expected_input_types
                    )
                except ValueError as e:
                    raise ValidationError(str(e), expected_name, expected_input_type)
        return user_inputs, sub_expected_input_types

    def validate(self, expected_input, all_request_inputs):
        """
        Validate that a given expected input exists in the requested input collection
        """
        # Extract useful information from expected input
        expected_input_type = expected_input.annotation  # i.e. str, int etc.
        # i.e. Form, Query, Json etc.
        expected_delivery_type = expected_input.default
        # Check if an alias is given, otherwise use the input name
        if expected_delivery_type.alias:
            expected_name = expected_delivery_type.alias
        else:
            expected_name = expected_input.name
        # Get input type as string to recognize typing objects, e.g. to convert typing.List to "typing.List"
        # Note: We use this str() method, as typing API is too unreliable, see https://stackoverflow.com/a/52664522/7173479
        expected_input_type_str = str(expected_input.annotation)

        # original_expected_input_type and expected_input_type_str will mutate throughout program,
        # so we need to keep the original for error messages
        original_expected_input_type = expected_input.annotation
        original_expected_input_type_str = expected_input_type_str

        # Expected delivery types can be a list if using MultiSource
        expected_delivery_types = [expected_delivery_type]
        if type(expected_delivery_type) is MultiSource:
            expected_delivery_types = expected_delivery_type.sources

        for source_index, source in enumerate(expected_delivery_types):
            # Validate that the expected delivery type is valid
            if source.__class__ not in all_request_inputs.keys():
                raise InvalidParameterTypeError(source)

            # Validate that user supplied input in expected delivery type (unless specified as Optional)
            user_input = all_request_inputs[source.__class__].get(
                expected_name
            )
            if user_input is None:
                # If default is given, set and continue
                if source.default is not None:
                    user_input = source.default
                else:
                    # Optionals are Unions with a NoneType, so we should check if None is part of Union __args__ (if exist)
                    if (
                            hasattr(expected_input_type, "__args__") and type(None) in expected_input_type.__args__
                            and source_index == len(expected_delivery_types) - 1  # If MultiSource, only return None for last source
                    ):
                        return user_input
                    else:
                        if len(expected_delivery_types) == 1:
                            raise MissingInputError(
                                expected_name, source.__class__
                            )
                        elif source_index != len(expected_delivery_types) - 1:
                            continue
                        else:
                            raise MissingInputError(
                                expected_name, source.__class__
                            )

            # Skip validation if typing.Any is given
            if expected_input_type_str.startswith("typing.Any"):
                return user_input

            user_inputs, expected_input_types = self._generic_types_validation_helper(expected_name, expected_input_type, expected_input_type_str, user_input, source)

            # Validate that user type(s) match expected type(s)
            validation_success = all(
                type(inp) in expected_input_types for inp in user_inputs
            )

            # Validate that if lists are required, lists are given
            if any(expected_input_type_str.startswith(list_hint) for list_hint in list_type_hints):
                if type(user_input) is not list:
                    validation_success = False

            # Error if types don't match
            if not validation_success:
                if hasattr(
                        original_expected_input_type, "__name__"
                ) and not (original_expected_input_type_str.startswith("typing.") or original_expected_input_type_str.startswith("list")):
                    type_name = original_expected_input_type.__name__
                else:
                    type_name = original_expected_input_type_str
                raise ValidationError(
                    f"must be type '{type_name}'",
                    expected_name,
                    original_expected_input_type,
                )

            # Validate parameter-specific requirements are met
            try:
                if type(user_input) is list:
                    source.validate(user_input)
                else:
                    source.validate(user_inputs[0])
            except ValueError as e:
                raise ValidationError(str(e), expected_name, expected_input_type)

            # Return input back to parent function
            if any(expected_input_type_str.startswith(list_hint) for list_hint in list_type_hints):
                return user_inputs
            return user_inputs[0]
