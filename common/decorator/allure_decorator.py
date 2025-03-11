from functools import wraps

from common.allure.allure_tools import allure_step


def allure_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result.is_decorator:
            # 添加allure步骤
            allure_step("请求URL: ", result.req_url)
            allure_step("请求方式: ", result.req_method)
            allure_step("请求头: ", str(result.req_headers))
            allure_step("请求数据: ", str(result.req_body))
            allure_step("响应断言数据: ", str(result.yaml_assert_data))
            allure_step("响应耗时(ms): ", str(result.res_runtime))
            allure_step("响应结果: ", result.res_data)
        return result
    return inner_wrapper
