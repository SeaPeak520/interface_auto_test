#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from common.allure.allure_report_data import AllureFileClean
from common.exceptions.exceptions import SendMessageError, ValueTypeError
from models.allure_model import TestMetrics
from utils import config
from utils.context import Context


class WeChatSend:
    """
    企业微信消息通知
    """

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.headers = {"Content-Type": "application/json"}

    def send_text(self, content, mentioned_mobile_list=None):
        """
        发送文本类型通知
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        :return:
        """
        _data = {"msgtype": "text", "text": {"content": content, "mentioned_list": None,
                                             "mentioned_mobile_list": mentioned_mobile_list}}

        if mentioned_mobile_list is not None and not isinstance(
                mentioned_mobile_list, list
        ):
            raise ValueTypeError("手机号码列表必须是list类型.")
            # 判断手机号码列表中得数据类型，如果为int类型，发送得消息会乱码
        if len(mentioned_mobile_list) >= 1:
            for i in mentioned_mobile_list:
                if not isinstance(i, str):
                    raise ValueTypeError("手机号码必须是字符串类型.")
                res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
                if res.json()['errcode'] != 0:
                    # ERROR.logger.error(res.json())
                    raise SendMessageError("企业微信「文本类型」消息发送失败")

    def send_markdown(self, content):
        """
        发送 MarkDown 类型消息
        :param content: 消息内容，markdown形式
        :return:
        """
        _data = {"msgtype": "markdown", "markdown": {"content": content}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            # ERROR.logger.error(res.json())
            raise SendMessageError("企业微信「MarkDown类型」消息发送失败")

    def _upload_file(self, file):
        """
        先将文件上传到临时媒体库
        """
        key = config.wechat.webhook.split("key=")[1]
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data).json()
        return res['media_id']

    def send_file_msg(self, file):
        """
        发送文件类型的消息
        @return:
        """

        _data = {"msgtype": "file", "file": {"media_id": self._upload_file(file)}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            # ERROR.logger.error(res.json())
            raise SendMessageError("企业微信「file类型」消息发送失败")

    def send_wechat_notification(self):
        """ 发送企业微信通知 """
        text = f"""【{config.project_name}自动化通知】
                                    >测试环境：<font color=\"info\">{config.env}</font>
                                    >测试负责人：@{config.tester_name}
                                    >
                                    > **执行结果**
                                    ><font color=\"info\">成  功  率  : {self.metrics.pass_rate}%</font>
                                    >用例  总数：<font color=\"info\">{self.metrics.total}</font>                                    
                                    >成功用例数：<font color=\"info\">{self.metrics.passed}</font>
                                    >失败用例数：`{self.metrics.failed}个`
                                    >异常用例数：`{self.metrics.broken}个`
                                    >跳过用例数：<font color=\"warning\">{self.metrics.skipped}个</font>
                                    >用例执行时长：<font color=\"warning\">{self.metrics.time} s</font>
                                    >时间：<font color=\"comment\">{Context.get_time()}</font>
                                    >
                                    >非相关负责人员可忽略此消息。
                                    >测试报告，点击查看>>[测试报告入口](http://:9999/index.html)"""
        WeChatSend(AllureFileClean().get_case_count()).send_markdown(text)


if __name__ == '__main__':
    WeChatSend(AllureFileClean().get_case_count()).send_wechat_notification()
