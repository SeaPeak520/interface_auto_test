#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import List, Text

from config import ALLURE_TESTCASES, ALLURE_SUMMARY
from models.allure_model import TestMetrics
from utils.json_control import get_all_allure_cases_path


class AllureFileClean:
    """allure 报告数据清洗，提取业务需要得数据"""

    @classmethod
    def get_testcases(cls) -> List:
        """ 获取所有 allure 报告中执行用例的情况"""
        # 将所有数据都收集到files中
        files = []
        for i in get_all_allure_cases_path(ALLURE_TESTCASES):
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                files.append(date)
        return files

    def get_failed_case(self) -> List:
        """ 获取到所有失败的用例标题和用例代码路径"""
        return [
            (i['name'], i['fullName'])
            for i in self.get_testcases()
            if i['status'] in ['failed', 'broken']
        ]

    def get_failed_cases_detail(self) -> Text:
        """ 返回所有失败的测试用例相关内容 """
        date = self.get_failed_case()
        values = ""
        # 判断有失败用例，则返回内容
        if len(date) >= 1:
            values = "失败用例:\n" + "        **********************************\n"
            for i in date:
                values += f"        {i[0]}:{i[1]}" + "\n"
        return values

    @classmethod
    def get_case_count(cls) -> "TestMetrics":
        """ 统计用例数量
        从allure的summary.json获取数据
        """
        try:
            with open(ALLURE_SUMMARY, 'r', encoding='utf-8') as file:
                data = json.load(file)
            _case_count = data['statistic']
            _time = data['time']
            keep_keys = {"passed", "failed", "broken", "skipped", "total"}
            # run_case_data: {'failed': 1, 'broken': 0, 'skipped': 0, 'passed': 0, 'total': 1}
            run_case_data = {k: v for k, v in data['statistic'].items() if k in keep_keys}
            # 判断运行用例总数大于0
            if _case_count["total"] > 0:
                # 计算用例成功率 (成功+跳过)/总
                run_case_data["pass_rate"] = round(
                    (_case_count["passed"] + _case_count["skipped"]) / _case_count["total"] * 100, 2
                )
            else:
                # 如果未运行用例，则成功率为 0.0
                run_case_data["pass_rate"] = 0.0
            # 收集用例运行时长
            run_case_data['time'] = _time if run_case_data['total'] == 0 else round(_time['duration'] / 1000, 2)
            return TestMetrics(**run_case_data)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "程序中检查到您未生成allure报告，"
                "通常可能导致的原因是allure环境未配置正确，"
            ) from exc


if __name__ == '__main__':
    # print(AllureFileClean().get_testcases())
    # print(AllureFileClean().get_failed_case())
    # print(AllureFileClean().get_case_count())
    a = AllureFileClean()
    print(a.get_testcases())
    print(a.get_failed_case())
    print(a.get_failed_cases_detail())
    print(a.get_case_count())
