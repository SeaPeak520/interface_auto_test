from functools import wraps

from common.requests.teardown_control import TearDownControl


def teardown_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result.is_decorator:
            TearDownControl(res=result).is_teardown()
        return result
    return wrapper
