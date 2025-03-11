import ast
from typing import Text, Dict, List, Any

from common.cache.local_cache_control import CacheHandler
from common.db.mysql_control import SqlHandler
from utils.regular_control import regular_handler, teardown_regular

from models.request_model import ResponseData, ParamPrepare, SendRequest, DependentType
from utils.json_control import jsonpath_get_value,jsonpath_replace


class TearDownControl:
    """ 处理依赖相关的业务 """

    def __init__(self, res: ResponseData):
        self._teardown = res.yaml_teardown
        self._teardown_sql = res.yaml_teardown_sql

    def get_cache(self, case_id: Text) -> Dict:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id: 用例id
        :return: 缓存用例池中的数据
        """
        return CacheHandler.get_cache(case_id)

    def request_send(self, yaml_case) -> ResponseData:
        """
        进行接口请求
        :param yaml_case: 从缓存中获取的yaml_case数据
        :return: ResponseData
        """
        from common.requests.request_send import RequestSend
        _yaml_case = regular_handler(str(yaml_case))
        result = RequestSend(_yaml_case).http_request(is_decorator=False)
        return result

    def param_prepare_replace_key(self, yaml_case: Dict, replace_key: List) -> Dict:
        """
        :param yaml_case: 从缓存中获取的yaml_case数据
        :param replace_key: 要正则匹配替换参数的信息，['$.data.applyId|13']
        :return: 正则替换后的数据
        """
        _yaml_case =yaml_case
        if replace_key is not None:
            for i in replace_key:
                _exp, v = i.split('|')
                if '$' in v:
                    _value = teardown_regular(str(v))
                    _yaml_case = jsonpath_replace(obj=_yaml_case, expression=_exp, new_value=_value)
                else:
                    _yaml_case = jsonpath_replace(obj=_yaml_case, expression=_exp, new_value=v)

        return _yaml_case

    def teardown_sql_handler(self) -> List:
        """
        对后置sql进行处理
        :return: sql的执行结果集合
        """
        CacheHandler.update_cache(cache_name='cid', value=61)
        s = SqlHandler()
        _regular_sql = ast.literal_eval(teardown_regular(str(self._teardown_sql)))
        _sql_result = s.sql_handler(_regular_sql)
        return _sql_result

    def param_prepare_handler(self, param_prepare: "ParamPrepare", case_id: Text) -> None:
        """
        param_prepare数据处理入口
        :param param_prepare: param_prepare数据
        :param case_id: 用例id
        :return:
        """
        _replace_key = param_prepare.replace_key
        _params = param_prepare.params
        # 通过case_id获取用例数据
        _yaml_case = self.get_cache(case_id)
        if _replace_key is not None:
            # 接口请求前判断是否需要替换用例的请求参数值
            _yaml_case = self.param_prepare_replace_key(_yaml_case, _replace_key)
        # 进行接口请求
        result = self.request_send(_yaml_case)
        if _params is not None:
            for i in _params:
                _dependent_type = i.dependent_type
                _jsonpath = i.jsonpath
                _set_cache = i.set_cache
                if _dependent_type == DependentType.SELF_RESPONSE.value:
                    _jsonpath_data = jsonpath_get_value(result.res_data, _jsonpath)
                    CacheHandler.update_cache(cache_name=_set_cache, value=_jsonpath_data)
                else:
                    raise TypeError('params.dependent_type不正确，只支持self_response')

    def send_request_type_input(self, yaml_case: Dict, expression: Text, new_value: Any) -> Dict:
        """
        :param yaml_case: 从缓存中获取的yaml_case数据
        :param expression: jsonpath表达式
        :param new_value: 替换的新数据
        :return:
        """
        _new_yaml_case = jsonpath_replace(yaml_case, expression, new_value)
        return _new_yaml_case

    def send_request_type_cache(self, yaml_case: Dict, replace_key: Text, cache_key: Text) -> Dict:
        """
        :param yaml_case: 从缓存中获取的yaml_case数据
        :param replace_key: jsonpath表达式匹配要的替换内容
        :param cache_key: 缓存key   int:cid
        :return: 替换后新的yaml_case数据
        """

        _cache_data = None
        if ':' in cache_key:
            _type, _key = cache_key.split(':')
            _value = CacheHandler.get_cache(_key)
            _cache_data = eval(f'{_type}({_value})')
        else:
            _cache_data = CacheHandler.get_cache(cache_key)
        _new_yaml_case = jsonpath_replace(obj=yaml_case, expression=replace_key, new_value=_cache_data)

        return _new_yaml_case

    def send_request_type_sqlData(self, yaml_case: Dict, replace_key: Text, data: Text, sql_result: List) -> Dict:
        """
        :param yaml_case: 从缓存中获取的yaml_case数据
        :param replace_key: jsonpath表达式匹配要的替换内容
        :param data: 从sql结果中使用jsonpath匹配数据， 0|0|$.alert_level
        :param sql_result: sql执行结果集合
        :return:
        """
        _yaml_case = yaml_case
        if sql_result:
            # k1 代表teardown_sql第几条sql，对应sql_result的第几个结果
            # k2 代表从sql_data的第几个数据
            # v 代表在sql_data的匹配规则
            _k1, _k2, _jsonpath = data.split('|')
            _sql_data = sql_result[int(_k1)]
            _value = jsonpath_get_value(_sql_data[int(_k2)], _jsonpath)
            # 在_yaml_case 中匹配符合 _replace_key的数据 并替换成_value
            _yaml_case = jsonpath_replace(obj=_yaml_case, expression=replace_key, new_value=_value)
        return _yaml_case

    def send_request_handler(self, send_request: List["SendRequest"], case_id: Text, sql_result: List) -> None:
        """
        send_request数据处理入口
        :param send_request: send_request的数据
        :param case_id:  用例id
        :param sql_result: teardown_sql执行结果集合
        :return:
        """
        _yaml_case = self.get_cache(case_id)
        for i in send_request:
            _dependent_type = i.dependent_type
            _replace_key = i.replace_key
            _data = i.data

            if _dependent_type == DependentType.INPUT.value:
                _yaml_case = self.send_request_type_input(_yaml_case, _replace_key, _data)

            elif _dependent_type == DependentType.CACHE.value:
                _yaml_case = self.send_request_type_cache(_yaml_case, _replace_key, _data)

            elif _dependent_type == DependentType.SQL_DATA.value:
                _yaml_case = self.send_request_type_sqlData(_yaml_case, _replace_key, _data, sql_result)

            else:
                raise TypeError('send_request.dependent_type不正确，只支持sqlData、input、cache')

            # 发起请求
            self.request_send(_yaml_case)

    def is_teardown(self) -> None:
        """
        判断是否有后置数据需要处理
        teardown和teardown_sql数据处理的总入口
        :return:
        """
        _sql_result = []
        if self._teardown_sql is not None:
            _sql_result = self.teardown_sql_handler()

        if self._teardown is not None:
            for teardown_data in self._teardown:
                _case_id = teardown_data.case_id
                _param_prepare = teardown_data.param_prepare
                _send_request = teardown_data.send_request

                if _param_prepare is not None:
                    self.param_prepare_handler(_param_prepare, _case_id)
                if _send_request is not None:
                    self.send_request_handler(_send_request, _case_id, _sql_result)


if __name__ == '__main__':
    from config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData
    from models.request_model import TestCase

    yaml_path = TESTDATA_DIR / 'xiaofa/练习/ArticleList.yaml'
    c = CaseData(yaml_path)
    _yaml_data = c.case_process()
    # print(_yaml_data[0])
    yaml_data = TestCase(**_yaml_data[0])
    # print(yaml_data)
    # print(yaml_data.teardown)
    TearDownControl(yaml_data.teardown).is_teardown()
    # b = a['teardown'][0]
    # teardown_data = TearDown(**b)
    # print(teardown_data)
