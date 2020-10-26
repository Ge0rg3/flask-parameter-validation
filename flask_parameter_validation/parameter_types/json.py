"""
    JSON data values
"""
from .parameter import Parameter


class Json(Parameter):
    name = "json"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)
