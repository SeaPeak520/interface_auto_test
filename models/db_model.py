from enum import Enum


class SetupTeardownType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    INSERT = "INSERT"
    DELETE = "DELETE"
    SELECT = "SELECT"
    UPDATE = "UPDATE"
    NUM = 'NUM'