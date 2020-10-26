#!/usr/bin/env python

import typing
from inspect import signature
from .parameter_types import Route, Json, Query, Form, File
from flask import request


class ValidateParameters:

    def default_error_function(self, error_message):
        return {
            "error": error_message,
        }, 400

    def __init__(self, error_function=None):
        if error_function is not None:
            self.error_function = error_function
        else:
            self.error_function = self.default_error_function

    def __call__(self, f):
        decorator_self = self

        def nested_func(**kwargs):
            parsed_inputs = {}
            # Get all request inputs as dicts
            request_inputs = {
                Route: kwargs.copy(),
                Json: request.json or {},
                Query: request.args.to_dict(),
                Form: request.form.to_dict(),
                File: request.files.to_dict()
            }
            # Get function arguments
            function_args = signature(f).parameters
            # Iterate through all
            for arg in function_args.values():
                param_type = arg.default  # ie. Route(), Json()
                param_name = arg.name  # ie. id, username
                param_annotation = arg.annotation or typing.Any  # ie. str, int
                # Ensure param type is valid
                if param_type.__class__ not in request_inputs.keys():
                    return self.error_function("Invalid parameter type.")

                # Get user input for given param type and name
                user_input = request_inputs[param_type.__class__].get(
                    param_name
                )

                # If default is given, set it
                if user_input is None and param_type.default is not None:
                    user_input = param_type.default

                # If no default and no input, error
                elif user_input is None:
                    ptype = param_type.name
                    return self.error_function(
                        f"Required {ptype} parameter '{param_name}' not given."
                    )

                # If typing's Any, ClassVar or Optional, don't validate type
                if isinstance(param_annotation, typing._SpecialForm):
                    valid = True
                    allowed_types = ["all"]

                # Otherwise, validate type
                else:
                    allowed_types = []
                    # If List or Union, get all "inner" types
                    if hasattr(param_annotation, "__args__"):
                        allowed_types = param_annotation.__args__
                    else:
                        allowed_types = (param_annotation,)

                    # Check if type matches annotation
                    annotation_is_list = False
                    if hasattr(param_annotation, "_name"):
                        annotation_is_list = param_annotation._name == "List"
                    if type(user_input) == list and annotation_is_list:
                        # If input is a list, validate all items
                        valid = all(
                            isinstance(i, allowed_types) for i in user_input
                        )
                    else:
                        # If not list, just validate singular data type
                        valid = isinstance(user_input, allowed_types)

                # Continue or error depending on validity
                if valid:
                    try:
                        param_type.validate(user_input)
                        parsed_inputs[param_name] = user_input
                    except Exception as e:
                        return self.error_function(
                            f"Parameter '{param_name}' {e}"
                        )
                else:
                    types = "/".join(t.__name__ for t in allowed_types)
                    return decorator_self.error_function(
                        f"Parameter '{param_name}' should be type {types}."
                    )

            return f(**parsed_inputs)

        nested_func.__name__ = f.__name__
        return nested_func
