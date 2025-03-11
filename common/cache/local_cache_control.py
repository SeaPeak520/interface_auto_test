#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地缓存处理
"""
from common.exceptions.exceptions import ValueNotFoundError

_cache_config = {}

class CacheHandler:
    @staticmethod
    def get_cache(cache_data):
        try:
            return _cache_config[cache_data]
        except KeyError as e:
            raise ValueNotFoundError(f"{cache_data}的缓存数据未找到，请检查是否将该数据存入缓存中") from e

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache_config[cache_name] = value
