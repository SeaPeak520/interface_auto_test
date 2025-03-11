from enum import Enum
from typing import Union, Text, List

from pydantic import BaseModel


class NotificationType(Enum):
    """ 自动化通知方式 """
    DEFAULT = '0'
    DING_TALK = '1'
    WECHAT = '2'
    EMAIL = '3'
    FEI_SHU = '4'

class Host(BaseModel):
    gateway_host: Union[Text, None]
    lawyer_host: Union[Text, None]
    callback_host: Union[Text, None]
    lianxi_host: Union[Text, None]


class MySqlDB(BaseModel):
    switch: bool = False
    host: Union[Text, None] = None
    user: Union[Text, None] = None
    pwd: Union[Text, None] = None
    port: Union[int, None] = None
    db: Union[Text, None] = None


class RedisDB(BaseModel):
    host: Union[Text, None] = None
    pwd: Union[Text, None] = None
    port: Union[int, None] = None
    db: Union[int, None] = None


class Webhook(BaseModel):
    webhook: Union[Text, None]


class Email(BaseModel):
    host: Union[Text, None] = None
    port: Union[int, None] = None
    user: Union[Text, None] = None
    pwd: Union[Text, None] = None
    sender: Union[Text, None] = None
    receivers: Union[List, None] = None
    receivers_list: Union[List, None] = None
    to: Union[Text, None] = None


class DingTalk(BaseModel):
    webhook: Union[Text, None]
    secret: Union[Text, None]


class Config(BaseModel):
    project_name: Union[Text, None]
    env: Union[Text, None]
    host: "Host"
    tester_name: Union[Text, None]
    notification_type: int
    # excel_report: bool
    # 数据库
    mysql: "MySqlDB"
    redis: "RedisDB"
    # 通知
    ding_talk: "DingTalk"
    wechat: "Webhook"
    email: "Email"
    target: List
    # mirror_source: Text
    # real_time_update_test_cases: bool = False
