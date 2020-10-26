"""
    Query Parameters
    - i.e. sent in GET requests, /?username=myname
"""
from .Parameter import Parameter


class Query(Parameter):
    name = "query"

    def __init__(self, default=None, **kwargs):
        super().__init__(default, **kwargs)
