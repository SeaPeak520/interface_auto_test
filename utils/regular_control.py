import ast
import re

from utils.context import Context
from loguru import logger


def config_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换请求数据
    ${{host}}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(config_regular(), func_name)(value_name) 执行config_regular类的 func_name函数，传入value_name
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['gateway_host', 'callback_host']
            for key in key_list:
                func_name = '_'.join(key.split("_")[1:])  # host
                value_data = getattr(Context(), func_name)(key)  # 获取对应的域名https://gateway.com
                pattern = re.compile(r'\$\{\{func\}\}'.replace('func', key))
                target = re.sub(pattern, str(value_data), target)  # 把host替换成config文件的值
        return target

    except AttributeError:
        logger.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}", )
        raise
    except IndexError:
        logger.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：${{get_time}}")
        raise


def cache_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换缓存数据
    $cache{login_init}  $cache{int:login_init}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(Context(), func_name)(value_name) 执行Context类的 func_name函数，传入value_name
    """
    from common.cache.local_cache_control import CacheHandler
    try:
        # 正则获取 $cache{login_init}中的值 --> login_init
        regular_pattern = r"\$cache\{(.*?)\}"
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['login_init'] #int:login_init
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:','redis:']
            for key in key_list:
                # 符合value_types的类型
                if any(i in key for i in value_types) is True:
                    value_type = key.split(":")[0]
                    regular_data = key.split(":")[1]
                    if 'redis' in key:
                        from common.cache.redis_control import RedisHelper
                        r = RedisHelper()
                        pattern = re.compile(r'\$cache\{' + value_type + ":" + regular_data + r'\}')
                        cache_data = r.mget(regular_data)[0][0]
                    else:
                        pattern = re.compile(r'\$cache\{' + value_type + ":" + regular_data + r'\}')
                        cache_data = eval(f"{value_type}({CacheHandler.get_cache(regular_data)})")
                else:
                    pattern = re.compile(r'\$cache\{' + key + r'\}')
                    cache_data = CacheHandler.get_cache(key)
                # 使用sub方法，替换已经拿到的内容
                target = re.sub(pattern, str(cache_data), target)
        return target
    except AttributeError:
        logger.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}")
        raise
    except IndexError:
        logger.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：$cache{login_init}")
        raise


def teardown_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换缓存数据
    $td{login_init}  $td{int:login_init}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(Context(), func_name)(value_name) 执行Context类的 func_name函数，传入value_name
    """
    from common.cache.local_cache_control import CacheHandler
    try:
        # 正则获取 $cache{login_init}中的值 --> login_init
        regular_pattern = r"\$td\{(.*?)\}"
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['login_init'] #int:login_init
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            for key in key_list:
                if any(i in key for i in value_types) is True:
                    value_type = key.split(":")[0]
                    regular_data = key.split(":")[1]
                    pattern = re.compile(r'\$td\{' + value_type + ":" + regular_data + r'\}')
                    cache_data = eval(f"{value_type}({CacheHandler.get_cache(regular_data)})")
                else:
                    pattern = re.compile(r'\$td\{' + key + r'\}')
                    cache_data = CacheHandler.get_cache(key)
                # 使用sub方法，替换已经拿到的内容
                target = re.sub(pattern, str(cache_data), target)
        return target
    except AttributeError:
        logger.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}")
        raise
    except IndexError:
        logger.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：$td{login_init}")
        raise

def regular_handler(target: str) -> str:
    regular_target = config_regular(target)
    regular_target = cache_regular(regular_target)
    return ast.literal_eval(regular_target)


if __name__ == '__main__':
    from config import TESTDATA_DIR
    from utils import YamlHandler
    from common.cache.local_cache_control import CacheHandler

    file = TESTDATA_DIR / 'xiaofa/案源收藏/caseCollectAdd.yaml'
    CacheHandler.update_cache(cache_name='token', value='[1,2]')
    yaml_data = YamlHandler(file).get_yaml_data()
    print(yaml_data)
    print(config_regular(str(yaml_data)))
    # print(yaml_case_regular(yaml_data))
    # a = ast.literal_eval(cache_regular(yaml_data))
    # print(a)
    # print(type(a))
    # print(type(a['caseCollectAdd']['headers']['authorization']))

    CacheHandler.update_cache(cache_name='cid',value=61)
    t_sql = 'select * from user where id=$td{cid}'
    print(teardown_regular(t_sql))
