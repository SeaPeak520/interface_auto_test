import test_case
import pytest
import subprocess

from common.allure.allure_report_data import AllureFileClean
from common.file_tools.from_excel_write_yaml import FromExcelWriteYaml
from common.notification.ding_talk import DingTalkSendMsg
from common.notification.email_control import SendReport
from common.notification.wechat_send import WeChatSend
from utils import config
from utils.context import Context
from loguru import logger
from config import LOG_DIR, TESTCASE_DIR, ALLURE_REPORT, ALLURE_RESULT, JENKINS_ALLURE, TESTDATA_FILE
from common.file_tools.from_yaml_write_case import write_testcase
from models.config_model import NotificationType

if __name__ == "__main__":
    # 添加日志输出到文件和控制台
    logger.add(f"{LOG_DIR}/app{Context.get_today()}.log", rotation="500 MB", retention="10 days")  # 文件轮换及保留10天
    # 初始化用例
    # 通过excel写入yaml用例
    # e = FromExcelWriteYaml(TESTDATA_FILE)
    # e.write_yaml()
    # 通过yaml用例批量生成pytest执行的py文件
    write_testcase()

    args = [
        "-s",
        "-v",
        # "-n=2",  # 收集用例结果会出现重复执行的问题
        # "--reruns=1",
        # "--reruns-delay=2",
        f"{TESTCASE_DIR}/xiaofa/练习/test_ArticleList.py",
        # f"{ROOT_DIR}/test_case/xiaofa/小法法工服务评价/",
        # f"--alluredir={JENKINS_ALLURE}",
        f"--alluredir={ALLURE_RESULT}",
        "--clean-alluredir"
    ]
    # pytest执行
    pytest.main(args)

    # 本地执行使用，jenkins执行时注释
    cmd = f"D:\\allure-2.22.0\\bin\\allure generate {ALLURE_RESULT} -o {ALLURE_REPORT} -c {ALLURE_REPORT}"
    subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')

    # 通知
    # 获取allure报告的数据
    # allure_data = AllureFileClean().get_case_count()
    # notification_mapping = {
    #     # 钉钉通知
    #     NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
    #     # 企微通知
    #     NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
    #     # 邮件通知
    #     NotificationType.EMAIL.value: SendReport(allure_data).send
    # }
    # # i.strip()去掉左右空格
    # if config.notification_type != NotificationType.DEFAULT.value:
    #     notify_type = config.notification_type.split(",")
    #     for i in notify_type:
    #         notification_mapping.get(i.strip())()
