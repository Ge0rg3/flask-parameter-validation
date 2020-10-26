"""
    Route Parameters
    - Sent as part of a path, i.e. /user/<int:id>
"""
from .Parameter import Parameter


class Route(Parameter):
    name = "route"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)
