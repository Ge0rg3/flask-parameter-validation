"""
    Base Parameter class.
    Should only be used as child class for other params.
"""
import re
from datetime import datetime
import dateutil.parser as parser


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
        func=None,  # Callable: function performing a fully customized validation
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
                if not self.func(value):
                    raise ValueError(
                        f"value does not match the validator function."
                    )

        return True

    def convert(self, value, allowed_types):
        """Some parameter types require manual type conversion (see Query)"""
        # Datetime conversion
        if datetime in allowed_types:
            try:
                return parser.parse(str(value))
            except parser._parser.ParserError:
                pass
        return value
