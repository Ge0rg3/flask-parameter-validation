from flask_parameter_validation.parameter_types.parameter import Parameter


class MultiSource(Parameter):
    name = "multi_source"

    def __init__(self, sources: list[Parameter], default=None, **kwargs):
        self.sources = sources
        super().__init__(default, **kwargs)
