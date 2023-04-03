"""
    Base Parameter class.
    Should only be used as child class for other params.
"""
import re
from datetime import datetime, time, date
import dateutil.parser as parser

from flask_parameter_validation.exceptions import ValidationError


class Parameter:

    # Parameter initialisation
    def __init__(
        self,
        default=None,  # any: default parameter value
        min_str_length=None,  # int: min parameter length
        max_str_length=None,  # int: max parameter length
        min_list_length=None,  # int: min number of items in list
        max_list_length=None,  # int: max number of items in list
        min_int=None,  # int: min number (if val is int)
        max_int=None,  # int: max number (if val is int)
        whitelist=None,  # str: character whitelist
        blacklist=None,  # str: character blacklist
        pattern=None,  # str: regexp pattern
        func=None,  # Callable -> Union[bool, tuple[bool, str]]: function performing a fully customized validation
        datetime_format=None,  # str: datetime format string (https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
    ):
        self.default = default
        self.min_list_length = min_list_length
        self.max_list_length = max_list_length
        self.min_str_length = min_str_length
        self.max_str_length = max_str_length
        self.min_int = min_int
        self.max_int = max_int
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.pattern = pattern
        self.func = func
        self.datetime_format = datetime_format

    # Validator
    def validate(self, value):
        if type(value) is list:
            values = value
            # Min list len
            if self.min_list_length is not None:
                if len(value) < self.min_list_length:
                    raise ValueError(
                        f"must have at least {self.min_list_length} items."
                    )
            # Max list len
            if self.max_list_length is not None:
                if len(value) > self.max_list_length:
                    raise ValueError(
                        f"must have have a maximum of {self.max_list_length} items."
                    )
        else:
            values = [value]

        # Iterate through values given (or just one, if not list)
        for value in values:
            # Min length
            if self.min_str_length is not None:
                if len(value) < self.min_str_length:
                    raise ValueError(
                        f"must have at least {self.min_str_length} characters."
                    )
            # Max length
            if self.max_str_length is not None:
                if len(value) > self.max_str_length:
                    raise ValueError(
                        f"must have a maximum of {self.max_str_length} characters."
                    )
            # Whitelist
            if self.whitelist is not None:
                for char in str(value):
                    if char not in self.whitelist:
                        raise ValueError(
                            f"must contain only characters: {self.whitelist}"
                        )
            # Blacklist
            if self.blacklist is not None:
                for bad in self.blacklist:
                    if bad in str(value):
                        raise ValueError(
                            f"must not contain: {bad}"
                        )
            # Min int
            if self.min_int is not None:
                if int(value) < self.min_int:
                    raise ValueError(
                        f"must be larger than {self.min_int}."
                    )
            # Max int
            if self.max_int is not None:
                if int(value) > self.max_int:
                    raise ValueError(
                        f"must be smaller than {self.max_int}."
                    )

            # Regexp
            if self.pattern is not None:
                if not re.match(self.pattern, value):
                    raise ValueError(
                        f"pattern does not match: {self.pattern}."
                    )

            # Callable
            if self.func is not None:
                func_result = self.func(value)
                if type(func_result) is bool:
                    if not func_result:
                        raise ValueError(
                            f"value does not match the validator function."
                        )
                elif type(func_result) is tuple:
                    if len(func_result) == 2 and type(func_result[0]) is bool and type(func_result[1]) is str:
                        if not func_result[0]:
                            raise ValueError(
                                func_result[1]
                            )
                    else:
                        raise ValueError(
                            f"validator function returned incorrect type: {str(type(func_result))}, should return bool or (bool, str)"
                        )

        return True

    def convert(self, value, allowed_types):
        """Some parameter types require manual type conversion (see Query)"""
        # Datetime conversion
        if None in allowed_types and value is None:
            return value
        if datetime in allowed_types:
            if self.datetime_format is None:
                try:
                    return parser.parse(str(value))
                except parser._parser.ParserError:
                    pass
            else:
                try:
                    return datetime.strptime(str(value), self.datetime_format)
                except ValueError:
                    raise ValueError(
                        f"datetime format does not match: {self.datetime_format}"
                    )
                pass
        elif time in allowed_types:
            try:
                return time.fromisoformat(str(value))
            except ValueError:
                raise ValueError("time format does not match ISO 8601")
        elif date in allowed_types:
            try:
                return date.fromisoformat(str(value))
            except ValueError:
                raise ValueError("date format does not match ISO 8601")
        return value
