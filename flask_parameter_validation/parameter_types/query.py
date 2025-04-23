"""
    Query Parameters
    - i.e. sent in GET requests, /?username=myname
"""
import json
from enum import Enum

from .parameter import Parameter


class Query(Parameter):
    name = "query"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)

    def convert(self, value, allowed_types, current_error=None):
        """Convert query parameters to corresponding types."""
        print(f"value: {value}, type: {type(value)}")
        original_value = value
        error = None
        if type(value) is str:
            # int conversion done before dict to handle potential IntEnum
            if int in allowed_types:
                try:
                    enum_test = super().convert(value, allowed_types, current_error)
                    if issubclass(type(enum_test), Enum) and issubclass(type(enum_test), int):
                        return enum_test
                    return int(value)
                except ValueError or TypeError:
                    pass
            if dict in allowed_types:
                try:
                    return json.loads(value)
                except ValueError:
                    error = ValueError(f"invalid JSON")
            # float conversion
            if float in allowed_types:
                if not (type(value) is int and str(value) == original_value):  # If we've already converted an int and the conversion is exact, skip float conversion
                    try:
                        return float(value)
                    except ValueError:
                        pass
            # bool conversion
            if bool in allowed_types:
                try:
                    if value.lower() == "true":
                        return True
                    elif value.lower() == "false":
                        return False
                except AttributeError:
                    pass
        if type(value) is not str:
            error = None
        return super().convert(value, allowed_types, current_error=error)
