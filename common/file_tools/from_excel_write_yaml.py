import ast
from pathlib import Path

import pandas as pd

from config import TESTDATA_DIR
from models.request_model import ContentType
from utils.excel_control import ExcelControl
from utils.yaml_control import YamlHandler


class FromExcelWriteYaml(ExcelControl):

    def get_is_run(self, data):
        """
        判断值，返回bool值
        :param data:
        :return:  bool
        """
        if pd.isna(data):
            raise ValueError("是否运行字段不能为空，请填写'是'或'否'")
        if data == '否':
            return False
        else:
            return True

    def data_convert(self, data):
        """
        数据类型处理
        :param data:
        :return:
        """
        if pd.isna(data):
            return None
        else:
            return ast.literal_eval(data)

    def get_request_type(self, headers):
        """通过headers判断请求类型"""
        if headers is None or 'Content-Type' not in headers.keys():
            return 'params'

        if ContentType.JSON.value in headers['Content-Type']:
            return 'json'
        elif ContentType.PARAMS.value in headers['Content-Type']:
            return 'params'
        elif ContentType.DATA.value in headers['Content-Type']:
            return 'data'
        else:
            raise TypeError(f"未知的Content-Type ：{headers['Content-Type']}")

    def get_dependent_case(self, dependent_case_data, setup_sql):
        if dependent_case_data is None or setup_sql is None:
            return False
        else:
            return True

    def write_yaml(self):
        sheet_name_list = self.get_sheet_names()
        for sheet_name in sheet_name_list:
            if sheet_name not in ['template']:
                rows_data = self.get_rows_data(sheet_name=sheet_name)
                for row in rows_data:
                    if not pd.isna(row['请求地址']) and not pd.isna(row['请求头']) and not pd.isna(row['请求参数']):
                        _version = row['版本号']
                        module_name = row['模块']
                        function_name = row['功能']
                        _, case_name = row['用例名称'].split('test_')
                        case_title = row['用例标题']
                        _is_run = row['是否运行']
                        _method = row['请求方式']
                        _service_name = row['服务']
                        _url = row['请求地址']
                        # 因为读取到的都是str，所以非str类型需要用data_convert转换类型
                        _headers = self.data_convert(row['请求头'])
                        _request_data = self.data_convert(row['请求参数'])
                        _dependent_case_data = self.data_convert(row['关联用例数据'])
                        _setup_sql = self.data_convert(row['关联sql数据'])
                        _current_request_set_cache = self.data_convert(row['将请求或响应设置缓存'])
                        _assert_data = self.data_convert(row['断言参数'])
                        _assert_sql = self.data_convert(row['断言sql'])
                        _teardown = self.data_convert(row['后置关联数据'])
                        _teardown_sql = self.data_convert(row['后置sql数据'])
                        _yaml_case = {
                            "case_common": {
                                "allureEpic": _version,
                                "allureFeature": module_name,
                                "allureStory": function_name
                            },
                            f"{case_name}": {
                                "host": "${{" + _service_name + "}}",
                                "url": _url,
                                "method": _method,
                                "remark": case_title,
                                "is_run": self.get_is_run(_is_run),
                                "headers": _headers,
                                "requestType": self.get_request_type(_headers),
                                "requestData": _request_data,
                                "dependence_case": self.get_dependent_case(_dependent_case_data, _setup_sql),
                                "dependence_case_data": _dependent_case_data,
                                "setup_sql": _setup_sql,
                                "current_request_set_cache": _current_request_set_cache,
                                "assert_data": _assert_data,
                                "assert_sql": _assert_sql,
                                "teardown": _teardown,
                                "teardown_sql": _teardown_sql
                            }
                        }
                        yaml_file = TESTDATA_DIR / sheet_name / module_name / f"{case_name}.yaml"
                        if not Path.is_file(yaml_file):
                            YamlHandler(yaml_file).write_yaml_by_dict(_yaml_case)


if __name__ == '__main__':
    from config import TESTDATA_FILE

    e = FromExcelWriteYaml(TESTDATA_FILE)
    e.write_yaml()
    row_data_list = e.get_rows_data('Sheet1')



# class FromExcelWriteYaml:
#     def __init__(self):
#         # 创建excel对象
#         self.excel_handle = ExcelHandler(TESTDATA_FILE)
#
#     # 获取测试文件的sheet名称列表 ['iarna', 'Sheet4']
#     @property
#     def get_sheet(self):
#         return self.excel_handle.get_sheet
#
#     @staticmethod
#     def data_handler_json(data):
#         """数据判空处理并转换JSON格式"""
#         return json.dumps(data) if data else None
#
#     @staticmethod
#     def data_handler_dict(data):
#         """数据判空处理并转换DICT格式"""
#         return json.loads(data) if data else {}
#
#     @staticmethod
#     def data_convert(data):
#         """数据判空处理并使用ast.literal_eval转换格式，前后置sql字符串转换成列表"""
#         return ast.literal_eval(data) if data else None
#
#     @staticmethod
#     def data_handler_int(data):
#         """数据判空处理并转换INT格式"""
#         return int(data) if data else None
#
#     @staticmethod
#     def judge_is_null(data, is_null=False, message=''):
#         """数据是否允许为空，默认不能为空"""
#         try:
#             if not is_null and data or is_null:
#                 return data
#         except ValueNullError as e:
#             raise f"{message}数据不能为空： {e}" from e
#
#
#
#     @staticmethod
#     def data_handler_host(address):
#         """解析地址映射配置文件的host参数并提取"""
#         from utils import config
#         host = address.split('.com')[0] + '.com'
#         host_list = config.host.dict()
#         if any(i == host for i in host_list.values()):
#             key = list(host_list.keys())
#             values = list(host_list.values())
#             v_index = values.index(host)
#             return "${{" + key[v_index] + "}}"
#         else:
#             raise ValueNullError(f"host: {host} ,配置文件没有对应的host参数")
#
#     @staticmethod
#     def data_handler_url(address):
#         """解析地址提取URL"""
#         return address.split('.com')[-1]
#
#     @staticmethod
#     def data_handler_is_run(is_run):
#         if is_run and is_run == '是':
#             return True
#         elif is_run == '否':
#             return False
#         else:
#             return None
#
#     def write_yaml(self):
#         # 1、循环遍历sheet，过滤test目录，并创建目录到data下（当有用例时创建）
#         for sheet in self.get_sheet:  # sheet名称列表循环
#             if 'test' not in sheet:
#                 module_list = []
#                 # 获取sheet页的所有数据 并遍历
#                 for i in self.excel_handle.get_sheet_data(sheet_name=sheet):
#                     # 把当前sheet的模块列表
#                     if i['模块'] not in module_list:
#                         module_list.append(i['模块'])
#                         # 2、循环sheet内的excel数据
#                 ###1、按模块创建目录
#                 # print(module_list)
#                 for module in module_list:  # 模块列数据循环
#                     # 1、创建模块目录
#                     # E:\pythonProject\new\data\Sheet1\小法名律小程序
#                     module_yaml_path = ensure_path_sep(f"{TESTDATA_DIR}{sheet}/{module}")
#                     mk_dir(module_yaml_path)
#
#                     ###2、分析excel数据
#                     # 模块的所有数据
#                     module_all_data = self.excel_handle.get_sheet_data(sheet_name=sheet, module_name=module)
#
#                     # 获取当前模块的 功能列表
#                     function_list = []
#                     for module_data in module_all_data:
#                         if module_data['功能'] not in function_list:
#                             function_list.append(module_data['功能'])
#
#                     # 功能列表数据 ['保存律师退订短信信息接口', '保存订单谈案关联信息']
#                     for function_list_value in function_list:
#                         # 当前功能列的所有数据集合
#                         function_data = self.excel_handle.get_sheet_data(sheet_name=sheet,
#                                                                          func_name=function_list_value)
#
#                         # yaml名称  auto_call_saveUnsubscribeReason
#                         # 解析用例名称创建空的yaml文件
#                         case = function_data[0]['用例名称'].split('test_')[-1]
#                         if '_0' in case:
#                             case = case.split('_0')[0]
#                         case_path = f'{module_yaml_path}/{case}.yaml'
#                         create_file(case_path)
#
#                         #####1、通用公共数据(从功能列数据集合中取第一条数据)
#                         case_common = {
#                             "allureEpic": function_data[0]['版本号'],
#                             "allureFeature": function_data[0]['模块'],
#                             "allureStory": function_data[0]['功能']
#                         }
#
#                         case_data = {'case_common': case_common}
#
#                         for function_data_value in function_data:
#                             #####2、用例数据
#                             # 1、基础信息数据
#                             address = self.judge_is_null(function_data_value['请求地址'],
#                                                          message=f"{function_data_value['功能']}的请求地址")
#                             host = self.data_handler_host(address)
#                             url = self.data_handler_url(address)
#                             method = self.judge_is_null(function_data_value['请求方式'],
#                                                         message=f"{function_data_value['功能']}的请求方式")
#                             remark = self.judge_is_null(function_data_value['用例标题'], is_null=True)
#                             is_run = self.data_handler_is_run(function_data_value['是否运行'])
#                             headers = self.data_handler_dict(self.judge_is_null(function_data_value['请求头'],
#                                                                                 message=f"{function_data_value['功能']}的请求头"))
#                             dependence = self.judge_is_null(function_data_value['关联用例数据'], is_null=True)
#                             request_type = self.request_type_handler(headers)
#                             request_data = self.data_handler_dict(
#                                 self.judge_is_null(function_data_value['请求参数'], is_null=True))
#
#                             info_case = {
#                                 "host": host,
#                                 "url": url,
#                                 "method": method,
#                                 "remark": remark,
#                                 "is_run": is_run,
#                                 "headers": headers,
#                                 "requestType": request_type,
#                                 "requestData": request_data,
#                                 "dependence_case": None,
#                                 "dependence_case_data": None,
#                                 "setup_sql": None,
#                                 "database_assert_sql": None,
#                                 "database_assert_result": None,
#                                 "assert_data": None,
#                                 "current_request_set_cache": None,
#                                 "teardown_sql": None,
#                                 "teardown": None
#                             }
#                             # 关联数据处理
#                             if dependence:
#                                 info_case['dependence_case'] = True
#                                 info_case['dependence_case_data'] = self.data_handler_dict(dependence)
#
#                             # 数据库校验处理
#                             # 缺少不会入库 != ''兼容0的值
#                             if function_data_value['数据库校验语句'] and function_data_value['数据库校验结果'] != '':
#                                 info_case['database_assert_sql'] = function_data_value['数据库校验语句']
#                                 info_case['database_assert_result'] = function_data_value['数据库校验结果']
#
#                             # 2、校验数据
#                             assert_data = {}
#                             if status_code := function_data_value['校验状态码']:
#                                 assert_data["status_code"] = self.data_handler_int(status_code)
#
#                             # 检验字段集合
#                             # ['$.code', '$.message']
#                             assert_field_list = [function_data_value['校验字段1'], function_data_value['校验字段2']]
#                             for key, assert_field in enumerate(assert_field_list):
#                                 if assert_field:
#                                     assert_name = assert_field.split('.')[-1]
#                                     assert_data[assert_name] = {
#                                         "jsonpath": assert_field,
#                                         "type": '==',
#                                         "value": self.judge_is_null(function_data_value[f'校验内容{str(key + 1)}'],
#                                                                     message=f"{function_data_value['功能']}的{assert_field}"),
#                                         "AssertType": None,
#                                         "message": self.judge_is_null(
#                                             function_data_value[f'校验错误信息{str(key + 1)}'], is_null=True)
#                                     }
#                             if assert_data:
#                                 info_case['assert_data'] = assert_data
#
#                             #######3、前置数据处理
#                             if setup_execute_sql := self.data_convert(function_data_value['前置条件(要执行的sql)']):
#                                 info_case['setup_sql'] = setup_execute_sql
#
#                             #######4、请求或响应设置缓存
#                             if current_request_set_cache := self.data_handler_dict(function_data_value['将请求或响应设置缓存']):
#                                 info_case['current_request_set_cache'] = current_request_set_cache
#
#                             #######5、后置数据处理
#                             # 后置-执行sql处理
#                             if teardown_sql := self.data_convert(function_data_value['后置条件(要执行的sql)']):
#                                 info_case['teardown_sql'] = teardown_sql
#
#                             if teardown := self.data_handler_dict(function_data_value['后置条件(执行接口)']):
#                                 info_case['teardown'] = teardown
#
#                             # 把info信息写入case中
#                             case_data[function_data_value['用例名称'].split('test_')[-1]] = info_case
#
#                         # 用case数据写入yaml文件中
#                         YamlHandler(case_path).write_yaml_by_dict(case_data)


# if __name__ == '__main__':
#     # 读取excel文件生成yaml用例
#     FromExcelWriteYaml().write_yaml()
