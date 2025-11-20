import json
import sys
import asyncio
import functools
import inspect
import re
import uuid
from inspect import signature
from typing import Optional, Union, get_origin, get_args, Any, get_type_hints

import flask
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequest
from .exceptions import (InvalidParameterTypeError, MissingInputError,
                         ValidationError)
from .parameter_types import File, Form, Json, Query, Route, Parameter
from .parameter_types.multi_source import MultiSource

fn_list = dict()

# from 3.10 onwards, Unions written X | Y have the type UnionType
UNION_TYPES = [Union]
if sys.version_info >= (3, 10):
    from types import UnionType
    UNION_TYPES = [Union, UnionType]

if sys.version_info >= (3, 11):
    from typing import NotRequired, Required, is_typeddict
elif sys.version_info >= (3, 9):
    from typing_extensions import NotRequired, Required, is_typeddict

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

            # Step 3 - For Query params, find which parameters should be split y `,`
            split_csv = {}
            default_list_disable_query_csv = flask.current_app.config.get("FPV_LIST_DISABLE_QUERY_CSV", False)
            for name, param in expected_inputs.items():
                list_disable_query_csv = default_list_disable_query_csv
                if param.default.list_disable_query_csv is not None:
                    list_disable_query_csv = param.default.list_disable_query_csv
                split_csv[param.default.alias or name] = not list_disable_query_csv

            # Step 4 - Convert request inputs to dicts
            request_inputs = {
                Route: kwargs.copy(),
                Json: json_input or {},
                Query: self._to_dict_with_lists(request.args, split_csv),
                Form: self._to_dict_with_lists(request.form),
                File: self._to_dict_with_lists(request.files),
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
            self, multi_dict: ImmutableMultiDict, split_csv: Optional[dict[str, bool]] = None
    ) -> dict:
        dict_with_lists = {}
        for key, values in multi_dict.lists():
            list_values = []
            for value in values:
                if split_csv and key in split_csv and split_csv[key]:
                    list_values.extend(value.split(","))
                else:
                    list_values.append(value)
            dict_with_lists[key] = list_values[0] if len(list_values) == 1 else list_values
        return dict_with_lists

    def _generic_types_validation_helper(self, 
                                         expected_name: str,
                                         expected_input_type: type,
                                         user_input: Any,
                                         source: Parameter,
                                         other_union_allowed_types: list[type] = []) -> tuple[Any, bool]:
        """
        Perform recursive validation of generic types (Optional, Union, and List/list)
        and convert input. If input is invalid, a fully converted input is not garunteed.

        :param expected_name: the name of the parameter we are checking against
        :param expected_input_type: the type annotation of the parameter
        :param user_input: the API user's input
        :param source: the type of Parameter we are taking input from
        :param other_union_allowed_types: the other types that are unioned at this level.
            We check one type at a time, but the convert() method needs to know
            what else the user_input is allowed to be to convert properly.

        :return: tuple of format (converted user_input, validation_success)
        """
        # union
        if get_origin(expected_input_type) in UNION_TYPES:
            # check for unions (Optional is just a Union with None)
            sub_expected_input_types = expected_input_type.__args__
            # go through each type in the union and see if we get a match
            for sub_expected_input_type in sub_expected_input_types:
                sub_converted_input, sub_success = self._generic_types_validation_helper(expected_name, sub_expected_input_type, user_input, source, other_union_allowed_types=list(sub_expected_input_types))
                if sub_success:
                    return sub_converted_input, True
            return user_input, False

        # list
        elif get_origin(expected_input_type) is list or expected_input_type is list:
            if type(user_input) is not list:
                # check if we should try to work with strings
                if type(source) is not Form and type(source) is not Query:
                    return user_input, False
                # if using a source that supports multidict style lists,
                # give singletons the benefit of the doubt. they could still count
                # as single-element lists
                if type(user_input) is str and len(user_input) > 0:
                    try:
                        user_input = json.loads(user_input)
                        # check for a stringified list e.g. '[1, 2]'
                        if type(user_input) is not list:
                            user_input = [user_input]
                    except ValueError:
                        user_input = [user_input]
                else:
                    user_input = [user_input]

            # process
            if len(get_args(expected_input_type)) == 0:
                # expected type is just a bare list with no sub type
                # we set to Any instead of returning True so that the input can get converted
                sub_expected_input_type = Any
            else:
                sub_expected_input_type = get_args(expected_input_type)[0]
            if len(user_input) == 1 and user_input[0] == "":
                # treat arrays of a single empty string as an empty array to support the Query param &value=
                return [], True
            converted_list = []
            # go through and validate each item in the array
            for inp in user_input:
                sub_converted_input, sub_success = self._generic_types_validation_helper(expected_name, sub_expected_input_type, inp, source)
                if not sub_success:
                    return user_input, False
                converted_list.append(sub_converted_input)
            return converted_list, True

        # typeddict
        elif is_typeddict(expected_input_type):
            # check for a stringified dict (like from Query)
            if type(user_input) is str:
                try:
                    user_input = json.loads(user_input)
                except ValueError:
                    return user_input, False
            if type(user_input) is not dict:
                return user_input, False
            # check that we have all required keys
            for key in expected_input_type.__required_keys__:
                if key not in user_input:
                    return user_input, False

            # process
            converted_dict = {}
            # go through each user input key and make sure the value is the correct type
            for key, value in user_input.items():
                annotations = get_type_hints(expected_input_type)
                if key not in annotations:
                    # we are strict in not allowing extra keys
                    # if you want extra keys, use NotRequired
                    return user_input, False
                # get the Required and NotRequired decorators out of the way, if present                
                annotation_type = annotations[key]
                if get_origin(annotation_type) is NotRequired or get_origin(annotation_type) is Required:
                    annotation_type = get_args(annotation_type)[0]
                sub_converted_input, sub_success = self._generic_types_validation_helper(expected_name, annotation_type, value, source)
                if not sub_success:
                    return user_input, False
                converted_dict[key] = sub_converted_input
            return converted_dict, True

        # dict
        elif get_origin(expected_input_type) is dict or expected_input_type is dict:
            # check for a stringified dict (like from Query or Form)
            if type(user_input) is str and len(user_input) > 0:
                try:
                    user_input = json.loads(user_input)
                except ValueError:
                    return user_input, False
            # check for a normal dict
            if type(user_input) is not dict:
                return user_input, False

            # process
            if len(get_args(expected_input_type)) == 0:
                # expected type is just a bare dict with no sub types
                # we set to Any instead of returning True so that the input can get converted
                key_expected_input_type = Any
                val_expected_input_type = Any
            else:
                key_expected_input_type = get_args(expected_input_type)[0]
                val_expected_input_type = get_args(expected_input_type)[1]
            converted_dict = {}
            # go through and validate each key and value in the dict
            for key, val in user_input.items():
                key_converted_input, key_success = self._generic_types_validation_helper(expected_name, key_expected_input_type, key, source)
                val_converted_input, val_success = self._generic_types_validation_helper(expected_name, val_expected_input_type, val, source)
                if not key_success or not val_success:
                    return user_input, False
                converted_dict[key_converted_input] = val_converted_input
            return converted_dict, True

        # non-generics
        else:
            if expected_input_type is Any:
                return user_input, True

            try:
                # convert
                user_input = source.convert(
                    # include any other allowed types for proper conversion
                    user_input, [expected_input_type] + other_union_allowed_types
                )

                if expected_input_type is Any:
                    # Any should always return true, no matter the input
                    return user_input, True

                # the actual "primative" type check
                return user_input, type(user_input) is expected_input_type
            except ValueError as e:
                raise ValidationError(str(e), expected_name, expected_input_type)

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

        # original_expected_input_type will mutate throughout program,
        # so we need to keep the original for error messages
        original_expected_input_type = expected_input.annotation

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

            converted_user_input, validation_success = self._generic_types_validation_helper(expected_name, expected_input_type, user_input, source)

            # Validate parameter-specific requirements are met
            try:
                source.validate(converted_user_input)
            except ValueError as e:
                raise ValidationError(str(e), expected_name, expected_input_type)

            # Error if types don't match
            if not validation_success:
                type_name = str(original_expected_input_type)
                raise ValidationError(
                    f"must be type '{type_name}'",
                    expected_name,
                    original_expected_input_type,
                )

            return converted_user_input
