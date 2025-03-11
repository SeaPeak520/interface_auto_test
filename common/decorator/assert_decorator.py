from functools import wraps

from common.assertion.assert_control import AssertUtil


def assert_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result.is_decorator:
            AssertUtil(result).assert_handler()
        return result
    return wrapper
