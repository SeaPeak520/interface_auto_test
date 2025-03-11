from loguru import logger
from pathlib import Path

from config import TESTDATA_DIR, TESTCASE_DIR
from utils.yaml_control import GetYamlCaseData
from common.exceptions.exceptions import FileNotFound


# 读取yaml文件写入用例
def write_testcase():
    # 获取测试数据目录的所有yaml文件路径list
    yaml_file_list = GetYamlCaseData.get_all_yaml_case_path(TESTDATA_DIR)
    # 遍历list
    for yaml_file in yaml_file_list:
        # 把yaml_file路径的父级（即不包含文件名）进行分组
        yaml_parts = yaml_file.parent.parts
        # test文件的目录 #E:/pythonProject/new/test_case/Sheet4\案源收藏
        # Path(*yaml_parts[yaml_parts.index('data') + 1:]) 获取data目录之后的路径
        case_file_dir = TESTCASE_DIR / Path(*yaml_parts[yaml_parts.index('data')+1:])
        # test文件的路径 #E:/pythonProject/new/test_case/Sheet4\案源收藏/test_caseCollectAdd.py
        case_file_path = case_file_dir / f"test_{yaml_file.with_suffix('.py').name}"

        # 获取yaml文件数据
        yaml_data = GetYamlCaseData(yaml_file).get_yaml_case_data()
        #执行的用例list: ['case_common', 'caseCollectConcel']
        case_list = list(yaml_data.keys())
        case_list.remove("case_common")
        
        #用例不存在执行
        if not case_file_path.exists():
            # 如果目录不存在，复制文件会报错
            if not case_file_dir.exists():
                case_file_dir.mkdir(parents=True,exist_ok=True)
            # 用例的类名
            class_name = f'Test_{yaml_file.stem}'
            # 函数名
            function_name = f'test_{yaml_file.stem.lower()}'
            # py内容
            content = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import allure
import pytest

from common.file_tools.get_yaml_data_analysis import GetTestCase
from common.requests.request_send import RequestSend
from utils.regular_control import config_regular

case_id = {case_list}
TestData = GetTestCase.get_case_data(case_id)
re_data = ast.literal_eval(config_regular(str(TestData)))

@allure.epic("{yaml_data['case_common']['allureEpic']}")
@allure.feature("{yaml_data['case_common']['allureFeature']}")
class {class_name}:

    @allure.story("{yaml_data['case_common']['allureStory']}")
    @pytest.mark.parametrize('in_data', re_data, ids=[i['remark'] for i in TestData])
    def {function_name}(self, in_data):
        RequestSend(in_data).http_request()

            """
            try:
                with open(case_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f'新增用例：{case_file_path}')
            except FileNotFound as e:
                logger.error(f'新增用例错误，写入失败: {e}')




if __name__ == '__main__':
    write_testcase()
