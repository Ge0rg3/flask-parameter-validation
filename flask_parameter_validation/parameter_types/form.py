"""
    Values sent in a POST Form request
    - Typical data from an HTML form (non-json)
"""
from .parameter import Parameter


class Form(Parameter):
    name = "form"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)
