from enum import Enum, unique
from typing import Union, Text, Dict, List, Optional, Any

from pydantic import BaseModel


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTION = "OPTION"


class ContentType(Enum):
    JSON = "application/json"
    PARAMS = "application/form-data"
    DATA = "application/x-www-form-urlencoded"


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    RESPONSE = 'response'
    REQUEST = 'request'
    SQL_DATA = 'sqlData'
    CACHE = "cache"
    INPUT = "input"
    SELF_RESPONSE = 'self_response'


# 前置数据模型
class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Union[Text, None, list]
    set_cache: Union[Text, None, list]
    # replace_key: Union[Dict, None]


class DependentCaseData(BaseModel):
    case_id: Text
    replace_key: Union[List, None] = None
    dependent_data: Union[None, List[DependentData]] = None


# 设置缓存模型
class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Union[Text, List]
    set_cache: Union[Text, List]


# 后置数据模型
class Param(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Text


class ParamPrepare(BaseModel):
    replace_key: Union[List, None] = None
    params: Union[List[Param]] = None


class SendRequest(BaseModel):
    dependent_type: Text
    # jsonpath: Optional[Text]
    data: Any
    # set_cache: Optional[Text]
    replace_key: Text


class TearDown(BaseModel):
    case_id: Text
    param_prepare: Union[ParamPrepare, None] = None
    send_request: Optional[Union[List["SendRequest"], None]] = None


# 用例模型
class TestCase(BaseModel):
    case_id: Text
    url: Text
    method: Text
    remark: Text
    is_run: Optional[bool]
    headers: Union[None, Dict]
    requestType: Text
    requestData: Union[Dict, List, None]
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"]]] = None
    setup_sql: Union[None, List]
    assert_data: Union[Dict, None]
    assert_sql: Union[list, None]
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    teardown: Optional[Union[None, List["TearDown"], Text]] = None
    teardown_sql: Union[List, None] = None
    # sleep: Optional[Union[int, float]]


# 响应结果模型
class ResponseData(BaseModel):
    # yaml_is_run: Union[None, bool, Text]
    yaml_remark: Union[None, Text]
    yaml_assert_data: Union[None, Dict]
    yaml_assert_sql: Union[None, List]
    yaml_current_request_set_cache: Union[None, List]
    yaml_teardown: Optional[Union[None, List["TearDown"], Text]] = None
    yaml_teardown_sql: Union[List, None] = None

    req_url: Text
    req_method: Text
    req_headers: Dict
    req_body: Any

    res_data: Any
    res_cookie: Dict
    res_runtime: Union[int, float]
    res_status_code: int

    is_decorator: bool


# 用例数据校验模型
class TestCaseEnum(Enum):
    URL = ("url", True)
    HOST = ("host", True)
    METHOD = ("method", True)
    REMARK = ("remark", True)
    IS_RUN = ("is_run", True)
    HEADERS = ("headers", True)
    REQUEST_TYPE = ("requestType", True)
    REQUEST_DATA = ("requestData", True)
    DE_CASE = ("dependence_case", True)
    DE_CASE_DATA = ("dependence_case_data", False)
    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    SETUP_SQL = ("setup_sql", False)
    ASSERT_DATA = ("assert_data", True)
    ASSERT_SQL = ("assert_sql", False)
    TEARDOWN = ("teardown", True)
    TEARDOWN_SQL = ("teardown_sql", False)
    SLEEP = ("sleep", False)
