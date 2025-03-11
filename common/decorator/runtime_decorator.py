#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
from loguru import logger

"""
统计请求运行时长装饰器，如请求响应时间超时
程序中会输入红色日志，提示时间 http 请求超时，默认时长为 3000ms
"""


def execution_duration(timeout: int = 3000):
    """
    封装统计函数执行时间装饰器
    :param timeout: 函数预计运行时长
    :return:
    """

    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result.is_decorator:
                # 计算时间戳毫米级别，如果时间大于timeout，则打印 函数名称 和运行时间
                if result.res_runtime > timeout:
                    logger.warning(
                        f"""\n==============================================
                        \n测试用例执行时间较长,超过默认值: {timeout} ms，请关注.
                        \n函数运行时间: {result.res_runtime} ms
                        \n测试用例信息为: {result.yaml_remark}
                        \n===============================================""")
            return result

        return swapper

    return decorator
