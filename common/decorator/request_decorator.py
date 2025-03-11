from functools import wraps

from loguru import logger


# 接口请求装饰器
def request_information(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # 判断日志为开启状态，才打印日志
        if result.is_decorator:
            logger.info(f"\n======================================================\n"
                        f"用例标题: {result.yaml_remark}\n"
                        f"请求路径: {result.req_url}\n"
                        f"请求方式: {result.req_method}\n"
                        f"请求头:   {result.req_headers}\n"
                        f"请求内容: {result.req_body}\n"
                        f"接口响应内容: {result.res_data}\n"
                        f"接口响应时长: {result.res_runtime} ms\n"
                        f"Http状态码: {result.res_status_code}\n"
                        "=====================================================\n")
        return result
    return wrapper
