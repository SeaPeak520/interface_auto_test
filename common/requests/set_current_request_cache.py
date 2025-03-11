#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Text, List, Dict, Any

from common.cache.local_cache_control import CacheHandler
from utils.json_control import jsonpath_get_value


class SetCurrentRequestCache:
    """将用例中的请求或者响应内容存入缓存"""

    def __init__(self, current_request_set_cache: List, request_data: Dict, response_data: Dict) -> None:
        self._current_request_set_cache = current_request_set_cache
        self._request_data = request_data
        self._response_data = response_data

    def set_cache(self,cache_name: Text,cache_value: Any) -> None:
        """将响应结果存入缓存"""
        CacheHandler.update_cache(cache_name=cache_name, value=cache_value)

    def set_caches_main(self) -> None:
        """设置缓存"""
        for i in self._current_request_set_cache:
            _type = i.type
            _jsonpath = i.jsonpath
            _set_cache = i.set_cache
            if _type.lower() == 'request':
                _jsonpath_data = jsonpath_get_value(self._request_data, _jsonpath)
                self.set_cache(cache_name=_set_cache,cache_value=_jsonpath_data)
            elif _type.lower() == 'response':
                _jsonpath_data = jsonpath_get_value(self._response_data, _jsonpath)
                self.set_cache(cache_name=_set_cache,cache_value=_jsonpath_data)
            else:
                raise TypeError('仅支持类型：request或response，请输出正确的类型！')
