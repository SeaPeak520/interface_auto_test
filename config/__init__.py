from pathlib import Path

# 主目录
ROOT_DIR = Path(__file__).resolve().parent.parent

# 测试用例目录
TESTCASE_DIR = ROOT_DIR / 'test_case'

# 测试数据目录
TESTDATA_DIR = ROOT_DIR / 'data'

# 前置测试数据的目录
PRE_DATA_DIR = ROOT_DIR / 'data/pre'

# 配置文件目录
CONFIG_DIR = ROOT_DIR / 'config'

# 日志目录
LOG_DIR = ROOT_DIR / 'log'

# 测试数据文件
TESTDATA_FILE = TESTDATA_DIR / 'testdata.xlsx'

# cookie文件
COOKIE_FILE = TESTDATA_DIR / 'cookie.txt'

# token文件
TOKEN_FILE = PRE_DATA_DIR / 'token.yaml'

CONFIG_FILE = CONFIG_DIR / 'config.yaml'

ALLURE_DIR = ROOT_DIR / 'report'

ALLURE_RESULT = ALLURE_DIR / 'allure-results'

ALLURE_REPORT = ALLURE_DIR / 'allure-report'

ALLURE_TESTCASES = ALLURE_REPORT / 'data/test-cases'

ALLURE_SUMMARY = ALLURE_REPORT / 'widgets/summary.json'

# /var/jenkins_home/workspace/auto为 jenkins项目路径
JENKINS_PATH = Path('/var/jenkins_home/workspace/auto')

JENKINS_ALLURE = JENKINS_PATH / 'allure-results'
