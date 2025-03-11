import ast
import json
from typing import List, Dict, Text

from common.exceptions.exceptions import ValueNotFoundError, ValueTypeError
from common.cache.local_cache_control import CacheHandler
from utils.json_control import jsonpath_get_value, jsonpath_replace
from models.request_model import TestCase, ResponseData, DependentData, DependentType
from utils.regular_control import config_regular, cache_regular


class DependentCase:
    """ 处理依赖相关的业务 """

    def __init__(self, yaml_case: TestCase) -> None:
        self._yaml_case = yaml_case
        self._dependence_case_data = self._yaml_case.dependence_case_data
        self._setup_sql = self._yaml_case.setup_sql

    def get_cache(self, case_id: Text) -> Dict:
        """
        通过case_id获取到用例数据
        :param case_id:
        :return:
        """
        _yaml_case = CacheHandler.get_cache(case_id)
        return _yaml_case

    def replace_key_handler(self, case_id: Text, replace_key: List) -> Dict:
        """
        使用jsonpath来替换yaml_case值
        :param case_id: 用例id
        :param replace_key: 要替换用例信息的内容
        :return: 替换后新的yaml_case
        """
        _yaml_case = self.get_cache(case_id)
        if replace_key is not None:
            for i in replace_key:
                k, v = i.split('|')
                if '$' in v:
                    _value = cache_regular(str(v))
                    _yaml_case = jsonpath_replace(obj=_yaml_case, expression=k, new_value=_value)
                else:
                    _yaml_case = jsonpath_replace(obj=_yaml_case, expression=k, new_value=v)
        return _yaml_case

    def send_request(self, yaml_case: Dict) -> "ResponseData":
        """
        :return: 用例请求结果
        """
        from common.requests.request_send import RequestSend

        _new_yaml_case = ast.literal_eval(config_regular(str(yaml_case)))
        re_data = RequestSend(_new_yaml_case).http_request(is_decorator=False)
        return re_data

    def dependent_sql_handler(self) -> List:
        """
        处理dependent_sql，把sql执行结果返回
        :return: sql执行结果集合
        """
        from common.db.mysql_control import SqlHandler
        s = SqlHandler()
        _sql_result = s.sql_handler(sql=self._setup_sql)
        return _sql_result

    def _dependent_type_for_response(self, res_data: Dict, json_path: Text, set_cache: Text) -> None:
        """
        把响应结果中用jsonpath表达式匹配的值设置缓存
        :param res_data: 响应结果
        :param json_path: jsonpath表达式
        :param set_cache: 设置缓存的key
        :return:
        """

        _set_value = jsonpath_get_value(res_data, json_path)
        if set_cache is not None:
            CacheHandler.update_cache(cache_name=set_cache, value=_set_value)

    def _dependent_type_for_request(self, req_body: Dict, json_path: Text, set_cache: Text) -> None:
        """
        把请求参数中用jsonpath表达式匹配的值设置缓存
        :param req_body: 请求参数
        :param json_path: jsonpath表达式
        :param set_cache: 设置缓存的key
        :return:
        """
        _set_value = jsonpath_get_value(req_body, json_path)
        if set_cache is not None:
            CacheHandler.update_cache(cache_name=set_cache, value=_set_value)

    def _dependent_type_for_sqlData(
            self,
            dependent_data: List[DependentData], sql_result: List) -> None:
        """
        判断依赖类型为 sql，程序中的依赖参数从 数据库中提取数据
        @param dependent_data: 依赖的数据
        @param sql_result: sql执行的结果
        @return:
        """
        # 判断依赖数据类型，依赖 sql中的数据
        if sql_result:
            for i in dependent_data:
                _json_path = i.jsonpath
                _set_cache = i.set_cache
                k1, k2, v = _json_path.split('|')
                sql_data = sql_result[int(k1)]
                json_data = jsonpath_get_value(obj=sql_data[int(k2)], expression=v)
                if _set_cache is not None:
                    CacheHandler.update_cache(cache_name=_set_cache, value=json_data)

    def is_dependent(self) -> None:
        """
        判断是否有数据依赖
        :return:
        """
        sql_result = []
        try:
            if self._setup_sql is not None:
                sql_result = self.dependent_sql_handler()
            # 1、判断caseid是否为 self 或其他
            if self._dependence_case_data is not None:
                for dependence_case_data in self._dependence_case_data:
                    _case_id = dependence_case_data.case_id
                    _replace_key = dependence_case_data.replace_key
                    _dependent_data = dependence_case_data.dependent_data
                    if _case_id == 'self':
                        self._dependent_type_for_sqlData(dependent_data=_dependent_data, sql_result=sql_result)
                    else:
                        # 通过case_id执行接口请求，获取request或response
                        _yaml_case = self.replace_key_handler(_case_id, _replace_key)
                        _re_data = self.send_request(_yaml_case)
                        for i in _dependent_data:
                            _dependent_type = i.dependent_type
                            _json_path = i.jsonpath
                            _set_cache = i.set_cache
                            # 判断dependent_type为request
                            if _dependent_type == DependentType.REQUEST.value:
                                self._dependent_type_for_request(_re_data.req_body, _json_path, _set_cache)
                            # 判断dependent_type为response
                            elif _dependent_type == DependentType.RESPONSE.value:
                                self._dependent_type_for_response(_re_data.res_data, _json_path, _set_cache)
                            else:
                                raise ValueError(
                                    "依赖的dependent_type不正确，只支持request、response、sql依赖\n"
                                    f"当前填写内容: {_dependent_type}"
                                )
        except KeyError as exc:
            raise ValueNotFoundError(
                f"dependence_case_data依赖用例中，未找到 {exc} 参数，请检查是否填写"
                f"如已填写，请检查是否存在yaml缩进问题"
            ) from exc
        except TypeError as exc:
            raise ValueTypeError(
                "dependence_case_data下的所有内容均不能为空！"
                "请检查相关数据是否填写，如已填写，请检查缩进问题"
            ) from exc

    def get_dependent_data(self) -> "TestCase":
        """
        :return:
        """
        # 执行前置
        self.is_dependent()
        # 替换cache缓存,model_dump()把TestCase转成dict
        _regular_data = ast.literal_eval(cache_regular(str(self._yaml_case.model_dump())))
        return TestCase(**_regular_data)


if __name__ == '__main__':
    from config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData

    a = []
    file = f'{TESTDATA_DIR}xiaofa/案源收藏/caseCollectAdd.yaml'
    case_data = CaseData(file).case_process(case_id_switch=True)
    case_data = case_data[0]['caseCollectAdd']
    print(json.dumps(case_data))
    __yaml_case = TestCase(**case_data)
    print(__yaml_case)
    # DependentCase(__yaml_case).get_dependent_data()

    # print(json.dumps(case_data[0], ensure_ascii=False))
