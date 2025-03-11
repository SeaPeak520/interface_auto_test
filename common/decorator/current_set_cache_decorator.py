#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
from common.requests.set_current_request_cache import SetCurrentRequestCache


def current_set_cache(func):
    """
    请求接口后对数据进行缓存
    """

    @wraps(func)
    def swapper(*args, **kwargs):
        result = func(*args, **kwargs)
        _current_set_cache = result.yaml_current_request_set_cache
        _req_body = result.req_body
        _res_data = result.res_data
        if _current_set_cache is not None:
            SetCurrentRequestCache(current_request_set_cache=_current_set_cache, request_data=_req_body,
                                   response_data=_res_data).set_caches_main()
        return result

    return swapper
