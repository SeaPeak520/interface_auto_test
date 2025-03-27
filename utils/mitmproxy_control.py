import ast
from urllib.parse import urlparse, parse_qs

from mitmproxy import ctx,http
from typing import List, Text, Dict, Any, Tuple

import yaml
from pathlib import Path

class Counter:
    def __init__(self, filter_url: List, filename: Text = './data/proxy_data.yaml'):
        self.num = 0
        self.file = Path(filename)
        self.counter = 1
        # 需要过滤的 url
        self.url = filter_url

        self.config_host = {
            "gateway_host": "https://x.com",
            "lawyer_host": "https://x.com",
            "callback_host": "https://www.baidu.com",
            "lianxi_host": "https://www.wanandroid.com"
        }
        self.content_type ={
            "JSON" : "application/json",
            "PARAMS" : "application/form-data",
            "DATA" : "application/x-www-form-urlencoded"
        }

    def filter_url(self, url: Text) -> bool:
        """过滤url"""
        for i in self.url:
            # 判断当前拦截的url地址，是否是addons中配置的host
            if i in url:
                # 如果是，则返回True
                return True
        # 否则返回 False
        return False

    def get_case_id(self, url: Text) -> Text:
        """
        通过url，提取对应的user_id
        :param url:
        :return:
        """
        _url_path = str(url).split('?')[0]
        # 通过url中的接口地址，最后一个参数，作为case_id的名称
        _url = _url_path.split('/')
        return _url[-1]

    def get_host(self, url: Text):
        """
        解析 url
        :param url: https://ug.baidu.com/mcp/pc/pcsearch?a=1
        :return: ${{callback_host}}
        """

        host = None
        # 循环遍历需要过滤的hosts数据
        for i in self.url:
            # 这里主要是判断，如果我们conf.py中有配置这个域名，则用例中展示 ”${{host}}“，动态获取用例host
            # 匹配config.host的values值，返回key
            if i in url:
                for k,v in self.config_host.items():
                    if v == i:
                        host = f'${{{{{k}}}}}'
                #host = f'${{{{{next(k for k,v in self.config_host.items() if v==i)}}}}}'
            else:
                host = i
        return host

    def get_url_path(self, url: Text):
        """
        解析 url_path
        :param url:  https://ug.baidu.com/mcp/pc/pcsearch
        :return: /mcp/pc/pcsearch
        """
        url_path = None
        # 循环需要拦截的域名
        for path in self.url:
            if path in url:
                url_path = url.split(path)[-1]
        return url_path

    def get_url_handler(self, url: Text) -> Tuple:
        """
        将 url 中的参数 转换成字典
        :param url: /trade?tradeNo=&outTradeId=11
        :return: {“outTradeId”: 11}
        """
        result = None
        url_path = None
        for i in self.url:
            if i in url:
                query = urlparse(url).query
                # 将字符串转换为字典
                params = parse_qs(query)
                # 所得的字典的value都是以列表的形式存在，如请求url中的参数值为空，则字典中不会有该参数
                result = {key: params[key][0] for key in params}
                url = url[0:url.rfind('?')]
                url_path = url.split(i)[-1]
        return url_path,result

    def header_handle(self, header) -> Dict:
        """
        提取请求头参数
        :param header:
        :return:
        """
        # 这里是将所有请求头的数据，全部都拦截出来了
        # 如果公司只需要部分参数，可以在这里加判断过滤
        headers = {}
        for key, value in header.items():
            headers[key] = value
        return headers

    def get_request_type(self, headers):
        """通过headers判断请求类型"""
        if headers is None or 'Content-Type' not in headers.keys():
            return 'params'

        if self.content_type['JSON'] in headers['Content-Type']:
            return 'json'
        elif self.content_type['PARAMS'] in headers['Content-Type']:
            return 'params'
        elif self.content_type['DATA'] in headers['Content-Type']:
            return 'data'
        else:
            raise TypeError(f"未知的Content-Type ：{headers['Content-Type']}")

    def data_handle(self, dict_str) -> Any:
        """处理接口请求、响应的数据，如null、true格式问题"""
        try:
            if dict_str != "":
                if 'null' in dict_str:
                    dict_str = dict_str.replace('null', 'None')
                if 'true' in dict_str:
                    dict_str = dict_str.replace('true', 'True')
                if 'false' in dict_str:
                    dict_str = dict_str.replace('false', 'False')
                dict_str = ast.literal_eval(dict_str)
            if dict_str == "" or dict_str is None:
                dict_str = None
            return dict_str
        except Exception as exc:
            raise exc

    def response_code_handler(self, response):
        """
        处理接口响应，默认断言数据为code码，如果接口没有code码，则返回None
        @param response:
        @return:
        """
        if response is None:
            return None
        try:
            data = self.data_handle(response.text)
            return {"code": {"jsonpath": "$.code", "type": "==",
                             "value": data['code'], "AssertRange": None,"message": None}}
        except KeyError:
            return None
        except NameError:
            return None

    def yaml_cases(self, data: Dict):
        """
        写入 yaml 数据
        :param data: 测试用例数据
        :return:
        """
        # 判断目录不存在，则创建目录
        if not Path.is_dir(self.file.parent):
            self.file.parent.mkdir(parents=True, exist_ok=True)

        # 不添加则会写入null，作用：把None不写入值
        def represent_none(self, _):
            return self.represent_scalar('tag:yaml.org,2002:null', '')

        yaml.add_representer(type(None), represent_none, Dumper=yaml.SafeDumper)
        """把dict数据追加到yaml文件中"""
        with open(self.file, 'a', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, encoding='utf-8',
                           allow_unicode=True)
            f.write('\n')

    def request(self, flow: http.HTTPFlow):
        # 存放需要过滤的接口
        filter_url_type = ['.css', '.js', '.map', '.ico', '.png', '.woff', '.map3', '.jpeg', '.jpg']
        url = flow.request.url
        ctx.log.info("=" * 100)
        # 判断过滤掉含 filter_url_type 中后缀的 url
        if any(i in url for i in filter_url_type) is False:
            # 存放测试用例
            if self.filter_url(url):
                ctx.log.info("-" * 100)
                ctx.log.info(f"host: {self.get_host(url)}")
                ctx.log.info(f"url: {flow.request.url}")
                ctx.log.info(f"text: {flow.request.text}")
                ctx.log.info(f"headers: {flow.request.headers}")
                ctx.log.info(f"re_text: {flow.response}")
                ctx.log.info("-" * 100)


                case_id = self.get_case_id(url) + str(self.counter)
                method = flow.request.method
                headers = self.header_handle(flow.request.headers)
                data = self.data_handle(flow.request.text)
                response = flow.response
                _yaml_case = {
                    f"{case_id}": {
                        "host": self.get_host(url),
                        "url": self.get_url_path(url),
                        "method": method,
                        "remark": None,
                        "is_run": True,
                        "headers": headers,
                        "requestType": self.get_request_type(headers),
                        "requestData": data,
                        "dependence_case": None,
                        "dependence_case_data": None,
                        "setup_sql": None,
                        "current_request_set_cache": None,
                        "assert_data": self.response_code_handler(response),
                        "assert_sql": None,
                        "teardown": None,
                        "teardown_sql": None
                    }
                }
                # 判断如果请求参数时拼接在url中，提取url中参数，转换成字典
                if "?" in url:
                    _yaml_case[case_id]['url'] = self.get_url_handler(url)[0]
                    _yaml_case[case_id]['data'] = self.get_url_handler(url)[1]
                #
                ctx.log.info("=" * 100)
                ctx.log.info(_yaml_case)
                #
                # 判断文件不存在则创建文件
                self.yaml_cases(_yaml_case)
                self.counter += 1

# 1、windows设置里需要配置代理，默认端口为: 8080
# mitmdump mitmweb
# 2、控制台输入 mitmdump -s ./utils/mitmproxy_control.py - p 8888   命令开启代理模式进行录制

addons = [
    Counter(['https://www.baidu.com'])
]

# if __name__ == '__main__':
#     c = Counter(['https://www.baidu.com'])
#     print(c.get_host("https://www.baidu.com/mcp/pc/pcsearch"))