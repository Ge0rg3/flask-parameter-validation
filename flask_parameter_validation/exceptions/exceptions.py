class MissingInputError(Exception):
    """Called if a user doesn't suppy a mandatory input"""
    def __init__(self, expected_name, expected_type):
        self.message = f"Missing required {expected_type.name} parameter '{expected_name}'."
        super().__init__(expected_type.name, expected_name)

    def __str__(self):
        return self.message

class InvalidParameterTypeError(Exception):
    """Called if the developer supplies a non-standard parameter type"""
    def __init__(self, invalid_type):
        self.message = (
            f"Invalid parameter type '{str(invalid_type)}' selected. "
            "Please refer to the flask-parameter-validation documentation."
        )
        super().__init__(self.message)

class ValidationError(Exception):
    """Called if parameter validation fails""" 
    def __init__(self, error_string, input_name, input_type):
        self.message = (
            f"Parameter '{input_name}' {error_string}"
        )
        super().__init__(error_string, input_name, input_type)
    
    def __str__(self):
        return self.message