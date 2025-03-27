#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import time
import allure
import pytest

from typing import List
from loguru import logger

from models.request_model import TestCase
from common.allure.allure_tools import allure_step
from utils.file_control import del_path

@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    from config import ALLURE_DIR
    del_path(ALLURE_DIR)


# @pytest.fixture(scope='session', autouse=True)
# def set_token():
#     # 通过yaml获取 case数据
#     _yaml_case = CaseData(TOKEN_FILE).case_process(case_id_switch=False)
#     # 发送请求
#     _re_data = RequestSend(_yaml_case).http_request(is_decorator=False)
#     _token_data = f"Bearer {jsonpath_get_value(_re_data.res_data, '$.data.token.token')}"
#     # 处理返回结果
#     CacheHandler.update_cache(cache_name='token', value=_token_data)


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if in_data is False:
        allure.dynamic.title(in_data.remark)
        allure_step(f"请求URL: ", in_data.url)
        allure_step(f"请求方式: ", in_data.method)
        allure_step("请求头: ", str(in_data.headers))
        allure_step("请求数据: ", str(in_data.requestData))
        allure_step("依赖数据: ", str(in_data.dependence_case_data))
        allure_step("预期数据: ", str(in_data.assert_data))
        pytest.skip()


def pytest_collection_modifyitems(items: List["Item"]) -> None:
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode-escape')
        # 目录包含中文会乱码，使用正则匹配处理单独处理unicode
        regular_pattern = r"\[(.*?)]"
        if key_list := re.findall(regular_pattern, item._nodeid):
            for key in key_list:
                value = key.encode('utf-8').decode('unicode-escape')
                pattern = re.compile(regular_pattern)
                item._nodeid = re.sub(pattern, f"[{str(value)}]", item._nodeid)
        # item._nodeid = item.nodeid.encode('utf-8').decode('unicode-escape')

    # 期望用例顺序
    # test_updatelawyerrelease 为用例名称，py文件里的函数
    # 例 ：appoint_items = ["test_updatelawyerrelease"]
    appoint_items = []

    # 指定运行顺序
    # items = [<Function test_deletelawyerrelease[删除曝光接口]>, <Function test_getlawyerreleaselistbyh5[小程序查询接口]>]
    run_items = []  # [<Function test_updatelawyerrelease[更新小法律师曝光]>]
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)  # 0 在run_items里的索引
        items_index = items.index(i)  # 5  在item里的索引
        # 期待运行索引与实际运行索引不同，则替换执行位置
        if run_index != items_index:
            items[items_index], items[run_index] = items[run_index], items[items_index]


# 如果使用多线程会有统计问题
def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    logger.info(f"用例总数: {_TOTAL}")
    logger.info(f"成功用例数：{_PASSED}")
    logger.info(f"异常用例数: {_ERROR}")
    logger.info(f"失败用例数: {_FAILED}")
    logger.info(f"跳过用例数: {_SKIPPED}")
    logger.info(f"用例执行时长: {_TIMES:.2f} s")
    try:
        _RATE = _PASSED / _TOTAL * 100
        logger.info(f"用例成功率: {_RATE:.2f} %")
    except ZeroDivisionError:
        logger.info("错误，用例成功率: 0.00 %")
