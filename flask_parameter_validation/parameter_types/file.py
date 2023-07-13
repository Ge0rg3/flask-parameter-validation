"""
    Files passed in a POST.
    - Would originally be in Flask's request.file
    - Value will be a FileStorage object
"""
from .parameter import Parameter


class File(Parameter):
    name = "file"

    def __init__(
        self,
        default=None,  # FileStorage object: default file
        content_types=None,  # List[str]: Valid content types
        min_length=None,  # Minimum file content-length
        max_length=None  # Maximum file content-length
    ):
        super().__init__(default)
        self.content_types = content_types
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        # Content type validation
        if self.content_types is not None:
            # We check mimetype, as it strips charset etc.
            if value.mimetype not in self.content_types:
                valid_types = "'" + "'/'".join(self.content_types) + "'"
                raise ValueError(f"must have content-type {valid_types}.")

        # Min content length validation
        if self.min_length is not None:
            if value.content_length < self.min_length:
                raise ValueError(
                    f"must have a content-length larger than {self.min_length}."
                )

        # Max content length validation
        if self.max_length is not None:
            if value.content_length > self.max_length:
                raise ValueError(
                    f"must have a content-length smaller than {self.max_length}."
                )
        return True
