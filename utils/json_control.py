import json
from pathlib import Path
from jsonpath import jsonpath
from jsonpath_ng import parse
from typing import Dict, Any


class JsonHandler:
    def __init__(self, file):
        self._file = file
        if not Path.is_file(self._file):
            raise FileNotFoundError(f"{self._file}文件不存在")

    # 获取json文件的内容，返回dict格式
    def get_json_data(self) -> dict[str, str | dict]:
        """
        :param dataFile: json文件路径
        :return:
        """
        with open(self._file, "r", encoding='utf-8') as f:
            # 先读取文件中字符串到str_f，再用json.loads(str_f)函数把字符串转换为数据结构
            str_f = f.read()
            dic = json.loads(str_f) if len(str_f) > 0 else {}
        f.close()
        return dic

    # 设置json文件，dic的键存在于dataFile中则替换值，不存在则新增键值
    def set_json_data(self, dic: dict) -> None:
        """
        :param dataFile: json文件路径
        :param dic: 匹配内容：存在则替换，不存在则新建,拿两个dict数据比较
        :return:
        """
        fir = self.get_json_data()  # 文件的
        sec = dic  # 接口获取的

        fir_keylist = set(fir.keys())  # 文件的key集合
        sec_keylist = set(sec.keys())  # 接口的key集合

        for sec_key in sec_keylist:  # 循环接口的key集合
            # 如果接口获取的key在文件的key集合里,执行
            # 如果接口获取的key不在文件的key集合里，则新增对应的keyvalue
            if (
                    sec_key in fir_keylist
                    and fir[sec_key] != sec[sec_key]
                    or sec_key not in fir_keylist
            ):  # 则判断对应key的value是否相同
                fir[sec_key] = sec[sec_key]

        with open(self._file, "w+", encoding='utf-8') as f:
            json.dump(fir, f)
            f.close()


# 获取某个目录下的所有yaml文件的路径
def get_all_allure_cases_path(file_path):
    """
    :param file_path: 路径
    :return: file_path目录下的所有文件路径
    """
    allure_cases_path = []
    for path in file_path.rglob("*.json"):
        allure_cases_path.append(path)

    return allure_cases_path


def jsonpath_get_value(obj: Dict, expression: str) -> Any:
    """
    用 JSONPath 定位并匹配数据的值
    :param obj: 原始json数据
    :param expression: 表达式，例：$.param_prepare[0].param_value
    :return:
    """
    _value = jsonpath(obj, expression)
    return _value[0]


def jsonpath_replace(obj: Dict, expression: str, new_value: Any) -> Dict:
    """
    用 JSONPath 定位并替换数据中的值
    :param obj: 原始json数据
    :param expression: jsonpath表达式，例：$.param_prepare[0].param_value
    :param new_value:  替换值
    :return:
    """
    jsonpath_expr = parse(expression)
    matches = jsonpath_expr.find(obj)
    for match in matches:
        # 替换匹配到的值
        if isinstance(match.context.value, list):  # 处理列表索引
            match.context.value[match.path.index] = new_value
        else:  # 处理字典键
            match.full_path.update(obj, new_value)
    return obj


if __name__ == '__main__':
    # 用法
    from config import TESTDATA_DIR, ALLURE_TESTCASES

    print(get_all_allure_cases_path(ALLURE_TESTCASES))
    a = {'a': 1, "b": 2}
    b = jsonpath_replace(a,'$.a',2)
    print(b)
    print(jsonpath_get_value(a, '$.a'))
