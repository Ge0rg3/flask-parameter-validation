"""
    Base Parameter class.
    Should only be used as child class for othe params.
"""


class ValidationError(Exception):
    pass


class Parameter:

    # Parameter initialisation
    def __init__(
        self,
        default=None,  # any: default parameter value
        min_length=None,  # int: min parameter length
        max_length=None,  # int: max parameter length
        min_int=None,  # int: min number (if val is int)
        max_int=None,  # int: max number (if val is int)
        whitelist=None,  # str: character whitelist
        blacklist=None  # str: character blacklist
    ):
        self.default = default
        self.min_length = min_length
        self.max_length = max_length
        self.min_int = min_int
        self.max_int = max_int
        self.whitelist = whitelist
        self.blacklist = blacklist

    # Validator
    def validate(self, value):
        # Min length
        if self.min_length is not None:
            if len(value) < self.min_length:
                raise ValidationError(
                    f"must be at least {self.min_length} characters."
                )
        # Max length
        if self.max_length is not None:
            if len(value) > self.max_length:
                raise ValidationError(
                    f"must be a maximum of {self.max_length} characters."
                )
        # Whitelist
        if self.whitelist is not None:
            for char in str(value):
                if char not in self.whitelist:
                    raise ValidationError(
                        f"must contain only characters: {self.whitelist}"
                    )
        # Blacklist
        if self.blacklist is not None:
            for bad in self.blacklist:
                if bad in str(value):
                    raise ValidationError(
                        f"must not contain: {bad}"
                    )
        # Min int
        if self.min_int is not None:
            if int(value) < self.min_int:
                raise ValidationError(
                    f"must be larger than {self.min_int}."
                )
        # Max int
        if self.max_int is not None:
            if int(value) > self.max_int:
                raise ValidationError(
                    f"must be smaller than {self.max_int}."
                )
        return True
