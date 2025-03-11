#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Text, List
from pathlib import Path

from common.cache.local_cache_control import CacheHandler
from models.request_model import Method, RequestType, TestCase, TestCaseEnum
from utils.yaml_control import GetYamlCaseData
from common.exceptions.exceptions import FileNotFound


class CaseDataCheck:
    """
    yaml 数据解析, 判断数据填写是否符合规范
    """

    def __init__(self, file_path):
        self._file_path = file_path
        if Path.exists(self._file_path) is False:
            raise FileNotFound("用例文件未找到")
        self._case_data = None
        self._case_id = None

    def _assert(self, attr: Text):
        """
        检查model的所有参数是否在测试用例中
        :param attr:  models文件的TestCaseEnum的参数，例：url 或 host ...
        :return:
        """
        assert attr in self._case_data.keys(), (
            f"用例ID为 {self._case_id} 的用例中缺少 {attr} 参数，请确认用例内容是否编写规范."
            f"当前用例文件路径：{self._file_path}"
        )

    def check_params_exit(self):
        """
        读取models文件的TestCaseEnum，如果值为True则检查 参数是否在测试用例中
        :return:
        """
        # list(TestCaseEnum._value2member_map_.keys())
        # 输出 [('url', True), ('host', True), ('method', True)...]
        for enum in list(TestCaseEnum._value2member_map_.keys()):
            if enum[1]:
                self._assert(enum[0])

    def check_params_right(self, enum_name, attr):
        """
        判断attr是否在model对应的enum_name函数里
        例子：检查case_data的requestType
        :param enum_name: <enum 'RequestType'> 例：Method (model的类)
        :param attr: data
        enum_name._member_names_ 输出RequestType类的所有name的列表(key)['JSON', 'PARAMS', 'DATA', 'FILE', 'EXPORT', 'NONE']
        :return: POST(大写attr)
        """

        _member_names_ = enum_name._member_names_
        assert attr.upper() in _member_names_, (
            f"用例ID为 {self._case_id} 的用例中 {attr} 值填写不正确，"
            f"当前框架中只支持 {_member_names_} 类型."
            f"如需新增 method 类型，请联系管理员."
            f"当前用例文件路径：{self._file_path}"
        )
        return attr.upper()

    @property
    def get_url(self) -> Text:
        """
        :return: host+url 例：https://xxx.com/mall-lawyer/case/collect/add
        """
        return self._case_data.get(TestCaseEnum.HOST.value[0]) + self._case_data.get(TestCaseEnum.URL.value[0])

    @property
    def get_method(self) -> Text:
        """
        :return: POST
        """
        # TestCaseEnum.METHOD.value[0]  method
        # self._case_data.get(TestCaseEnum.METHOD.value[0])) post（在测试数据中获取method的值）
        return self.check_params_right(
            Method,
            self._case_data.get(TestCaseEnum.METHOD.value[0])
        )

    @property
    def get_headers(self):
        return self._case_data.get(TestCaseEnum.HEADERS.value[0])

    @property
    def get_request_type(self):
        """
        传models的RequestType类 ，requestType
        :return: PARAMS
        """
        return self.check_params_right(
            RequestType,
            self._case_data.get(TestCaseEnum.REQUEST_TYPE.value[0])
        )

    @property
    def get_dependence_case_data(self):
        """
        判断是否有前置信息
        :return: 前置数据
        """
        if _dep_data := self._case_data.get(TestCaseEnum.DE_CASE.value[0]):
            assert self._case_data.get(TestCaseEnum.DE_CASE_DATA.value[0]) is not None, (
                f"程序中检测到您的 case_id 为 {self._case_id} 的用例存在依赖，但是 {_dep_data} 缺少依赖数据."
                f"如已填写，请检查缩进是否正确， 用例路径: {self._file_path}"
            )
        return self._case_data.get(TestCaseEnum.DE_CASE_DATA.value[0])

    @property
    def get_assert_data(self):
        """
        :return: 要校验断言的数据(ASSERT_DATA)
        """
        _assert_data = self._case_data.get(TestCaseEnum.ASSERT_DATA.value[0])
        assert _assert_data is not None, (
            f"用例ID 为 {self._case_id} 未添加断言，用例路径: {self._file_path}"
        )
        return _assert_data

    @property
    def get_assert_sql(self):
        """
        :return: 要校验断言的数据(ASSERT_DATA)
        """
        _assert_sql = self._case_data.get(TestCaseEnum.ASSERT_SQL.value[0])
        return _assert_sql


class CaseData(CaseDataCheck):
    """
        获取yaml文件的用例数据
    """

    def case_process(self, case_id_switch: bool = False) -> List:
        """
        :param case_id_switch: 是否包含case_id
        :return: 单个yaml文件的case数据列表
        """
        # 获取
        data = GetYamlCaseData(self._file_path).get_yaml_case_data()
        case_list = []
        for key, values in data.items():
            # 公共配置中的数据，与用例数据不同，需要单独处理
            if key != 'case_common':
                self._case_data = values
                self._case_id = key
                # 检查model参数是否在测试用例中
                super().check_params_exit()
                new_case_data = {
                    'case_id': key,
                    'url': self.get_url,
                    'method': self.get_method,
                    'is_run': self._case_data.get(TestCaseEnum.IS_RUN.value[0]),
                    'remark': self._case_data.get(TestCaseEnum.REMARK.value[0]),
                    'headers': super().get_headers,
                    'requestType': super().get_request_type,
                    'requestData': self._case_data.get(TestCaseEnum.REQUEST_DATA.value[0]),
                    'dependence_case': self._case_data.get(TestCaseEnum.DE_CASE.value[0]),
                    'dependence_case_data': self.get_dependence_case_data,
                    'setup_sql': self._case_data.get(TestCaseEnum.SETUP_SQL.value[0]),
                    "assert_data": self.get_assert_data,
                    "assert_sql": self.get_assert_sql,
                    "current_request_set_cache": self._case_data.get(TestCaseEnum.CURRENT_RE_SET_CACHE.value[0]),
                    # # "sleep": self._case_data.get(TestCaseEnum.SLEEP.value[0]),
                    "teardown": self._case_data.get(TestCaseEnum.TEARDOWN.value[0]),
                    "teardown_sql": self._case_data.get(TestCaseEnum.TEARDOWN_SQL.value[0])
                }
                # TestCase(**_case_data) 解包校验_case_data的内容（键、值类型）
                if case_id_switch is True:
                    case_list.append({key: TestCase(**new_case_data).model_dump()})
                else:
                    case_list.append(TestCase(**new_case_data).model_dump())
        return case_list


class GetTestCase:
    """
        用例执行时获取Cache数据
    """

    @staticmethod
    def get_case_data(case_id_lists: List) -> List:
        # 用例数据集合
        case_lists = []
        for i in case_id_lists:
            _data = CacheHandler.get_cache(i)
            case_lists.append(_data)
        return case_lists


if __name__ == '__main__':
    from config import TESTDATA_DIR

    yaml_path = TESTDATA_DIR / 'xiaofa/练习/ArticleList.yaml'
    print(yaml_path)
    # c = CaseDataCheck(yaml_path)
    # c.check_params_exit()
    # c.check_params_right(Method,'post1')
    # case_data = CaseData(file).case_process(case_id_switch=True)
    # print(json.dumps(case_data[0], ensure_ascii=False))
    c = CaseData(yaml_path)
    print(c.case_process(True))
