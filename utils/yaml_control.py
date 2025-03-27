import yaml
from pathlib import Path


class YamlHandler:
    def __init__(self, file: Path) -> None:
        self._file = file

    # 获取yaml文件数据
    def get_yaml_data(self) -> dict[str, str | dict]:
        """
        :return: 文件的dict数据
        """
        if not Path.is_file(self._file):
            raise FileNotFoundError(f"{self._file}文件不存在")

        with open(self._file, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def write_yaml_by_dict(self, dict_data):

        # 判断目录不存在，则创建目录
        if not Path.is_dir(self._file.parent):
            self._file.parent.mkdir(parents=True,exist_ok=True)

        # 不添加则会写入null，作用：把None不写入值
        def represent_none(self, _):
            return self.represent_scalar('tag:yaml.org,2002:null', '')

        yaml.add_representer(type(None), represent_none, Dumper=yaml.SafeDumper)
        """把dict数据全量写入到yaml文件中"""
        with open(self._file, 'w+', encoding='utf-8') as f:
            yaml.safe_dump(dict_data, f, default_flow_style=False, sort_keys=False, encoding='utf-8',
                           allow_unicode=True)


# 获取单个yaml文件的测试数据
class GetYamlCaseData(YamlHandler):
    def get_yaml_case_data(self):
        """
        获取yaml文件测试用例数据
        :return:
        """
        _yaml_data = self.get_yaml_data()
        return _yaml_data

    @staticmethod
    def get_all_yaml_case_path(file_path):
        """
        获取某个目录下的所有yaml文件的路径
        :param file_path: 路径
        :return: file_path目录下的所有文件路径
        """
        from utils import config
        yamlfile_path = []
        target_after = []
        # 1、过滤当前目录和文件
        # 获取当前目录的目录和文件
        for path in Path(file_path).iterdir():
            # 不存在过滤列表里则插入target_after中
            if path.name not in config.target:
                target_after.append(path)
        # 2、获取目录下的所有插入yamlfile_path
        # 因为target_after可能包含文件，所以判断文件插入yamlfile_path，是目录则遍历
        for _dir in target_after:
            if Path.is_dir(_dir):
                for path in _dir.rglob('*'):
                    if Path.is_file(path):
                        yamlfile_path.append(path)
            else:
                yamlfile_path.append(_dir)
        return yamlfile_path


if __name__ == '__main__':
    # 用法
    from config import TESTDATA_DIR

    path = TESTDATA_DIR / 'xiaofa/案源收藏/caseCollectAdd.yaml'
    # CacheHandler.update_cache(cache_name='token', value='[1,2]')
    a = GetYamlCaseData(path).get_yaml_case_data()

    print('------------')
    print(type(a), a)
    print(type(a['caseCollectAdd']['requestData']))
    print(type(a['caseCollectAdd']['requestData']['caseId']))
    print(GetYamlCaseData.get_all_yaml_case_path(TESTDATA_DIR))
    print('============')
