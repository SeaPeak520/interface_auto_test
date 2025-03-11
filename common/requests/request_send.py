import ast

import requests
import urllib3

from common.db.mysql_control import MysqlDB
from common.decorator.allure_decorator import allure_decorator
from common.decorator.assert_decorator import assert_decorator
from common.decorator.current_set_cache_decorator import current_set_cache
from common.decorator.request_decorator import request_information
from common.decorator.runtime_decorator import execution_duration
from common.decorator.teardown_decorator import teardown_decorator
from common.requests.denpendent_case import DependentCase
from models.request_model import TestCase, RequestType, ResponseData
from utils.regular_control import cache_regular


class RequestSend:
    def __init__(self, yaml_case):
        # 过滤InsecureRequestWarning警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # self._yaml_case = yaml_case
        self._yaml_case = TestCase(**yaml_case)

    @staticmethod
    def response_elapsed_total_seconds(res) -> float:
        """获取接口响应时长"""
        try:
            return round(res.elapsed.total_seconds() * 1000, 2)
        except AttributeError:
            return 0.00

    def request_type_for_json(
            self,
            **kwargs):
        """ 判断请求类型为json格式 传dict"""
        return requests.request(
            method=self._yaml_case.method,
            url=self._yaml_case.url,
            json=self._yaml_case.requestData,
            headers=self._yaml_case.headers,
            verify=False,
            **kwargs
        )

    def request_type_for_params(
            self,
            **kwargs):
        """处理 requestType 为 params 传dict"""
        return requests.request(
            method=self._yaml_case.method,
            url=self._yaml_case.url,
            params=self._yaml_case.requestData,
            headers=self._yaml_case.headers,
            verify=False,
            **kwargs
        )

    def request_type_for_data(
            self,
            **kwargs):
        """判断 requestType 为 data 类型"""
        return requests.request(
            method=self._yaml_case.method,
            url=self._yaml_case.url,
            data=self._yaml_case.requestData,
            headers=self._yaml_case.headers,
            verify=False,
            **kwargs
        )

    def _setup_sql_handler(self):
        """
        前置sql处理
        :return:
        """
        s = MysqlDB()
        for i in self._yaml_case.setup_sql:
            s.execute(i)

    def _check_params(
            self,
            response_data,
            yaml_case: "TestCase",
            is_decorator: bool = True
    ) -> "ResponseData":
        """
        :param res:
        :param yaml_data:
        :return: 处理接口返回及测试用例，返回一个通用的数据
        """
        _data = {
            "yaml_remark": yaml_case.remark,
            "yaml_assert_data": yaml_case.assert_data,
            "yaml_assert_sql": yaml_case.assert_sql,
            "yaml_current_request_set_cache": yaml_case.current_request_set_cache,
            "yaml_teardown": yaml_case.teardown,
            "yaml_teardown_sql": yaml_case.teardown_sql,

            "req_url": response_data.url,
            "req_method": response_data.request.method,
            "req_headers": response_data.request.headers,
            "req_body": yaml_case.requestData,

            "res_data": response_data.json(),
            "res_cookie": response_data.cookies,
            "res_runtime": self.response_elapsed_total_seconds(response_data),
            "res_status_code": response_data.status_code,

            "is_decorator": is_decorator

        }

        # 抽离出通用模块，判断 http_request 方法中的一些数据校验
        return ResponseData(**_data)

    @allure_decorator  # allure步骤装饰器
    @request_information  # 接口请求装饰器（打印请求信息日志）
    @teardown_decorator  # 后置处理装饰器
    @assert_decorator  # 断言装饰器
    @current_set_cache  # 缓存处理装饰器
    @execution_duration(3000)  # 封装统计函数执行时间装饰器
    def http_request(self, is_decorator=True) -> "ResponseData":
        """
        :param is_decorator: 用于判断是否执行装饰器，True执行，False不执行，主要用于关联接口时不需要执行装饰器
        :return:
        """
        # 判断yaml文件的is_run参数是否执行用例
        if self._yaml_case.is_run is True or self._yaml_case.is_run is None:
            # 如果有依赖数据统一在那边做处理
            # 如果有依赖，先执行前置信息并且进行缓存处理（在get_dependent_data函数里缓存处理）
            if self._yaml_case.dependence_case is True:
                if self._yaml_case.dependence_case_data is None and self._yaml_case.setup_sql is None:
                    raise ValueError("前置条件数据dependence_case_data或setup_sql为空，补充信息！！")
                self._yaml_case = DependentCase(self._yaml_case).get_dependent_data()
            else:
                # 如果没有前置，且yaml_case里面仍有缓存的参数，所以也要进行缓存处理
                _regular_data = ast.literal_eval(cache_regular(str(self._yaml_case.model_dump())))
                self._yaml_case = TestCase(**_regular_data)

            # 映射对应方法的内存地址
            # RequestType.JSON.value 输出 RequestType模型的JSON的值
            requests_type_mapping = {
                RequestType.JSON.value: self.request_type_for_json,
                RequestType.DATA.value: self.request_type_for_data,
                RequestType.PARAMS.value: self.request_type_for_params
                # RequestType.FILE.value: self.request_type_for_file,
                # RequestType.NONE.value: self.request_type_for_none,
                # RequestType.EXPORT.value: self.request_type_for_export
            }

            # 进行接口请求
            # requests_type_mapping.get(self._yaml_case.requestType) 执行的函数，比如JSON，执行request_type_for_json的函数
            response_data = requests_type_mapping.get(self._yaml_case.requestType)()

            # 判断用例关联依赖，不执行装饰器
            return (
                self._check_params(
                    response_data=response_data, yaml_case=self._yaml_case
                )
                if is_decorator
                else self._check_params(response_data=response_data, yaml_case=self._yaml_case, is_decorator=False)
            )


if __name__ == '__main__':
    # from common.config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData
    from config import TESTDATA_DIR

    file = TESTDATA_DIR / 'xiaofa/案源收藏/caseCollectAdd.yaml'

    case_data = CaseData(file).case_process(case_id_switch=False)
    _yaml_data = case_data[0]
    # print(yaml_data)
    RequestSend(_yaml_data).http_request()
