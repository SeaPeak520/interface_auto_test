from typing import Any, Text, Dict

import allure

from common.assertion import assert_type as assert_type
from common.exceptions.exceptions import AssertTypeError
from models import load_module_functions
from models.assert_model import AssertType, AssertRange
from models.request_model import ResponseData
from utils.json_control import jsonpath_get_value


class AssertUtil:
    def __init__(self, response_data: "ResponseData") -> None:
        """
        :param response_data：接口请求返回的信息

        self参数：
        _remark: 用例备注信息（打印日志）
         _assert_data: yaml文件中assert的数据
         _req_body:  yaml文件中requestData的数据
         _res_data:  请求接口返回的数据(响应数据)
         _status_code: 状态码
        """
        self._remark = response_data.yaml_remark
        self._assert_data = response_data.yaml_assert_data
        self._assert_sql = response_data.yaml_assert_sql
        self._req_body = response_data.req_body
        self._res_data = response_data.res_data
        self._status_code = response_data.res_status_code

    @property
    def get_assert_data(self) -> Dict[str, Any]:
        """
        获取assert_data的数据
        :return: {'stata_code': 200 , 'code': {'jsonpath': '$.code', 'type': '==', 'value': 200, 'AssertType': None, 'meassage': '状态码不一致'}}
        """
        # 校验self._assert_data数据不为空
        assert self._assert_data is not None, f"{self.__class__.__name__} 应该包含一个 assert data 属性"

        # return ast.literal_eval(str(self._assert_data))
        return self._assert_data

    @property
    def get_status_code(self) -> int:
        """
        获取断言描述，如果未填写，则返回 0
        :return:
        """
        return self.get_assert_data.get("status_code", 0)

    def get_jsonpath(self, data) -> Text:
        """
        获取data的 key为jsonpath的值
        :param data:{'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return: $.code
        """
        assert 'jsonpath' in data.keys(), f" 断言数据: {data} 中缺少 `jsonpath` 属性 "
        return data.get("jsonpath")

    def get_type(self, data) -> Text:
        """
        获取data中的type值
        :param data:{'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return: equals
        """
        # self.get_assert_data.get("type") 为'=='
        # AssertType(self.get_assert_data.get("type")).name 为 'equals'
        # AssertType('==') 表示通过值访问 ，等于AssertType.equals  输出：<enum 'AssertType'>
        assert 'type' in data.keys(), f" 断言数据: {data} 中缺少 `type` 属性 "
        return AssertType(data.get("type")).name

    def get_value(self, data) -> Any:
        """
        获取data的 key为value的值
        :param data:{'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return: 200
        """
        assert 'value' in data.keys(), f" 断言数据: {data} 中缺少 `value` 属性 "
        return data.get("value")

    def get_assert_range(self, data) -> Text:
        """
        获取assert_data的 key为AssertType的值
        :param data:{'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return: None
        """
        assert 'AssertRange' in data.keys(), f" 断言数据: {data} 中缺少 `AssertRange` 属性 "
        return data.get("AssertRange")

    def get_message(self, data) -> Text:
        """
        获取断言描述，如果未填写，则返回 `None`
        :param data:{'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return: code不一致
        """
        return data.get("message")

    def _assert(self, _type: Text, check_value: Any, expect_value: Any, message: Text = "") -> None:
        """
        断言处理入口
        :param _type: equals
        :param check_value:  要校验的值
        :param expect_value:  预期值
        :param message:  预期不符提示的信息
        :return: load_module_functions(assert_type)['equals']执行assert_type文件的equals方法
        load_module_functions(assert_type) 获取assert_type里所有方法的地址
        """
        load_module_functions(assert_type)[_type](check_value, expect_value, message)

    def assert_data_handler(self, data, assert_data) -> None:
        """
        通过$.code使用jsonpath获取到的数据，再进行断言
        :param data: 要使用jsonpath获取的数据
        :param assert_data: {'jsonpath': '$.code','type': '==','value': 200,'AssertRange': None,'message': 'code不一致'}
        :return:
        """
        _assert_value = jsonpath_get_value(data, self.get_jsonpath(assert_data))
        assert _assert_value is not False, (
            f"jsonpath数据提取失败，提取对象: {data} , 当前语法: {self.get_jsonpath}"
        )
        self._assert(_type=self.get_type(assert_data), check_value=_assert_value,
                     expect_value=self.get_value(assert_data),
                     message=f"{self.get_message(assert_data)}：实际值: {_assert_value},期望值: {self.get_value(assert_data)}")

    def _assert_sql_handler(self, assert_data) -> None:
        """
        对assertRange为SQL进行处理
        :param assert_data:
        :return:
        """
        if self._assert_sql is None:
            raise ValueError("assertRange为SQL时，assert_sql不能为空")

        from common.db.mysql_control import SqlHandler
        s = SqlHandler()
        _sql_result = s.sql_handler(sql=self._assert_sql)

        _jsonpath = self.get_jsonpath(assert_data)
        # 对jsonpath(0|0|$.id)进行处理
        _k1, _k2, _jp = _jsonpath.split('|')
        _sql_data = _sql_result[int(_k1)]
        _assert_value = jsonpath_get_value(_sql_data[int(_k2)], _jp)

        assert _assert_value is not False, (
            f"jsonpath数据提取失败，提取对象: {_sql_data[int(_k2)]} , 当前语法: {_jp}"
        )
        self._assert(_type=self.get_type(assert_data), check_value=_assert_value,
                     expect_value=self.get_value(assert_data),
                     message=f"{self.get_message(assert_data)}：实际值:{type(_assert_value)} {_assert_value},期望值:{type(self.get_value(assert_data))} {self.get_value(assert_data)}")

    @allure.step('进行断言检验')
    def assert_handler(self) -> None:
        """
        get_type 获取判断类型 equals
        _assert_resp_data   通过jsonpath在response_data匹配到的值
        get_value  yaml文件获取assert_data的 key为value的值
        get_message  yaml文件获取assert_data的 key为message的值
        :return:
        """
        # print(f"""=================
        # \n断言信息：{self._assert_data}
        # \n请求体： {self._req_body}
        # \n响应参数：{self._res_data}
        # \n状态码：{self._status_code}
        # """)
        for i in self.get_assert_data.keys():
            # try:
            if i == 'status_code':
                self._assert(_type='equals', check_value=self._status_code, expect_value=self.get_status_code,
                             message='状态码不一致')
            else:
                # _assert_data: {'jsonpath': '$.code', 'type': '==', 'value': 200, 'AssertType': None, 'meassage': '状态码不一致'}
                _assert_data = self.get_assert_data.get(i)
                _assert_range = self.get_assert_range(_assert_data)
                # 判断请求参数为响应数据断言
                if _assert_range is None or _assert_range.upper() == AssertRange.RESPONSE.value:
                    self.assert_data_handler(self._res_data, _assert_data)

                # 判断请求参数为请求数据断言
                elif _assert_range.upper() == AssertRange.REQUEST.value:
                    self.assert_data_handler(self._req_body, _assert_data)

                # 判断数据库断言
                elif _assert_range.upper() == AssertRange.SQL.value:
                    self._assert_sql_handler(_assert_data)

                else:
                    raise AssertTypeError(f"{self._remark} 断言失败，目前只支持数据库断言和响应断言")


if __name__ == '__main__':
    # print(AssertType('=='))
    # print(type(AssertType('==')))
    # print(AssertType('==').name)

    _data = {
        "yaml_remark": '添加收藏案源信息接口',
        "yaml_assert_data": {
            'status_code': 201,
            'code': {
                'jsonpath': '$.code',
                'type': '==',
                'value': 200,
                'AssertRange': 'Response',
                'message': 'code不一致'
            },
            'message': {
                'jsonpath': '$.message',
                'type': '==',
                'value': '操作成功1',
                'AssertRange': None,
                'message': 'message不一致'
            },
            'caseId': {
                'jsonpath': '$.caseId',
                'type': '==',
                'value': 18996,
                'AssertRange': 'Request1',
                'message': 'caseId不一致'
            },
            'caseId1': {
                'jsonpath': '$.caseId',
                'type': '==',
                'value': 18995,
                'AssertRange': 'Request',
                'message': 'caseId不一致'
            }
        },
        "yaml_current_request_set_cache": None
        ,

        "req_url": 'https://xxx.com',
        "req_method": 'POST',
        "req_headers": {
            'Content-Type': 'application/form-data',
            'authorization': 123
        },
        "req_body": {
            'caseId': 18995
        },

        "res_data": {"code": 200, "message": "操作成功", "data": "收藏成功"},
        "res_cookie": {},
        "res_runtime": 2.01,
        "res_status_code": 200,

        # "file": os.path.basename(__file__),
        "is_decorator": True

    }
    au = AssertUtil(ResponseData(**_data))
    au.assert_handler()

    # yaml_data = YamlHandler(ensure_path_sep('E:\\pythonProject\\new/data/test.yaml')).get_yaml_data()
    #
    # assert_data = yaml_data['caseCollectAdd']['assert']
    # response_data = '{"code":200,"message":"操作成功","data":"收藏成功"}'
    # # request_data = yaml_data['caseCollectAdd']['requestData']
    # status_code = 20
    #
    # au = AssertUtil(assert_data, response_data, status_code)
    # au.assert_type_handle()
