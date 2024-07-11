from typing import Type

from flask_parameter_validation.parameter_types.parameter import Parameter


class MultiSource(Parameter):
    name = "multi_source"

    def __init__(self, *sources: list[Type[Parameter]], **kwargs):
        self.sources = [Source(**kwargs) for Source in sources]
        super().__init__(**kwargs)
