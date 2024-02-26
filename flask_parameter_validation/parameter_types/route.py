"""
    Route Parameters
    - Sent as part of a path, i.e. /user/<int:id>
"""
from .parameter import Parameter


class Route(Parameter):
    name = "route"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)

    def convert(self, value, allowed_types):
        """Convert query parameters to corresponding types."""
        if type(value) is str:
            # int conversion
            if int in allowed_types:
                try:
                    value = int(value)
                except ValueError:
                    pass
            # float conversion
            if float in allowed_types:
                try:
                    value = float(value)
                except ValueError:
                    pass
            # bool conversion
            if bool in allowed_types:
                try:
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                except AttributeError:
                    pass

        return super().convert(value, allowed_types)