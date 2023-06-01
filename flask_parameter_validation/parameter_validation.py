import re

from .parameter_types import Route, Json, Query, Form, File
from .exceptions import MissingInputError, InvalidParameterTypeError, ValidationError
from flask import request
from inspect import signature
from werkzeug.exceptions import BadRequest


class ValidateParameters:

    def __init__(self, error_handler=None):
        self.custom_error_handler = error_handler

    def __call__(self, f):
        """
        Parent flow for validating each required parameter
        """
        def nested_func(**kwargs):
            # Step 1 - Combine all flask input types to one dict
            json_input = None
            if request.headers.get("Content-Type") is not None:
                if re.search("application/[^+]*[+]?(json);?", request.headers.get("Content-Type")):
                    try:
                        json_input = request.json
                    except BadRequest:
                        return {"error": "Could not parse JSON."}, 400
            request_inputs = {
                Route: kwargs.copy(),
                Json: json_input,
                Query: request.args.to_dict(),
                Form: request.form.to_dict(),
                File: request.files.to_dict()
            }
            # Step 2 - Get expected input details as dict
            expected_inputs = signature(f).parameters

            # Step 3 - Validate each expected input
            validated_inputs = {}
            for expected in expected_inputs.values():
                if self.custom_error_handler is None:
                    try:
                        new_input = self.validate(expected, request_inputs)
                    except MissingInputError as e:
                        return {"error": str(e)}, 400
                    except ValidationError as e:
                        return {"error": str(e)}, 400
                else:
                    try:
                        new_input = self.validate(expected, request_inputs)
                    except Exception as e:
                        return self.custom_error_handler(e)
                validated_inputs[expected.name] = new_input
            return f(**validated_inputs)

        nested_func.__name__ = f.__name__
        return nested_func

    def validate(self, expected_input, all_request_inputs):
        """
        Validate that a given expected input exists in the requested input collection
        """
        # Extract useful information from expected input
        expected_name = expected_input.name
        expected_input_type = expected_input.annotation  # i.e. str, int etc.
        # i.e. Form, Query, Json etc.
        expected_delivery_type = expected_input.default

        # Get input type as string to recognize typing objects, e.g. to convert typing.List to "typing.List"
        # Note: We use this str() method, as typing API is too unreliable, see https://stackoverflow.com/a/52664522/7173479
        expected_input_type_str = str(expected_input.annotation)

        # original_expected_input_type and expected_input_type_str will mutate throughout program,
        # so we need to keep the original for error messages
        original_expected_input_type = expected_input.annotation
        original_expected_input_type_str = expected_input_type_str

        # Validate that the expected delivery type is valid
        if expected_delivery_type.__class__ not in all_request_inputs.keys():
            raise InvalidParameterTypeError(expected_delivery_type)

        # Validate that user supplied input in expected delivery type (unless specified as Optional)
        user_input = all_request_inputs[expected_delivery_type.__class__].get(
            expected_name)
        if user_input is None:
            # If default is given, set and continue
            if expected_delivery_type.default is not None:
                user_input = expected_delivery_type.default
            else:
                # Optionals are Unions with a NoneType, so we should check if None is part of Union __args__ (if exist)
                if hasattr(expected_input_type, "__args__") and type(None) in expected_input_type.__args__:
                    return user_input
                else:
                    raise MissingInputError(
                        expected_name, expected_delivery_type.__class__)

        # Skip validation if typing.Any is given
        if expected_input_type_str.startswith("typing.Any"):
            return user_input

        # In python3.7+, typing.Optional is used instead of typing.Union[..., None]
        if expected_input_type_str.startswith("typing.Optional"):
            new_type = expected_input_type.__args__[0]
            expected_input_type = new_type
            expected_input_type_str_str = str(new_type)

        # Prepare expected type checks for unions, lists and plain types
        if expected_input_type_str.startswith("typing.Union"):
            expected_input_types = expected_input_type.__args__
            user_inputs = [user_input]
            # If typing.List in union and user supplied valid list, convert remaining check only for list
            for exp_type in expected_input_types:
                if str(exp_type).startswith("typing.List"):
                    if type(user_input) is list:
                        # Only convert if validation passes
                        if all(type(inp) in exp_type.__args__ for inp in user_input):
                            expected_input_type = exp_type
                            expected_input_types = expected_input_type.__args__
                            expected_input_type_str = str(exp_type)
                            user_inputs = user_input
        # If list, expand inner typing items. Otherwise, convert to list to match anyway.
        elif expected_input_type_str.startswith("typing.List"):
            expected_input_types = expected_input_type.__args__
            if type(user_input) is list:
                user_inputs = user_input
            else:
                user_inputs = [user_input]
        else:
            user_inputs = [user_input]
            expected_input_types = [expected_input_type]

        # Perform automatic type conversion for parameter types (i.e. "true" -> True)
        for count, value in enumerate(user_inputs):
            try:
                user_inputs[count] = expected_delivery_type.convert(
                    value, expected_input_types)
            except ValueError as e:
                raise ValidationError(str(e), expected_name, expected_input_type)

        # Validate that user type(s) match expected type(s)
        validation_success = all(
            type(inp) in expected_input_types for inp in user_inputs)

        # Validate that if lists are required, lists are given
        if expected_input_type_str.startswith("typing.List"):
            if type(user_input) is not list:
                validation_success = False

        # Error if types don't match
        if not validation_success:
            if hasattr(original_expected_input_type, "__name__") and not original_expected_input_type_str.startswith("typing."):
                type_name = original_expected_input_type.__name__
            else:
                type_name = original_expected_input_type_str
            raise ValidationError(
                f"must be type '{type_name}'", expected_name, original_expected_input_type)

        # Validate parameter-specific requirements are met
        try:
            expected_delivery_type.validate(user_input)
        except ValueError as e:
            raise ValidationError(str(e), expected_name, expected_input_type)

        # Return input back to parent function
        if len(user_inputs) == 1:
            return user_inputs[0]
        return user_inputs
