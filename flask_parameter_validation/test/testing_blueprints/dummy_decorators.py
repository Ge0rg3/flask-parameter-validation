"""
Decorators that do nothing and test if the ValidateParameters decorator breaks
other decorators upstream.
"""
from functools import wraps

def dummy_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

def dummy_async_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
