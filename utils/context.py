import ast
import datetime
import random


class Context:
    """ 正则替换 """

    def __init__(self):
        from faker import Faker
        self._faker = Faker(locale='zh_CN')

    @classmethod
    def random_int(cls) -> int:
        """
        :return: 随机数
        """
        return random.randint(0, 5000)

    def get_phone(self) -> str:
        """
        :return: 随机生成手机号码
        """
        return self._faker.phone_number()

    def get_id_number(self) -> str:
        """

        :return: 随机生成身份证号码
        """

        return self._faker.ssn()

    def get_female_name(self) -> str:
        """

        :return: 女生姓名
        """
        return self._faker.name_female()

    def get_male_name(self) -> str:
        """

        :return: 男生姓名
        """
        return self._faker.name_male()

    def get_email(self) -> str:
        """

        :return: 生成邮箱
        """
        return self._faker.email()

    @classmethod
    def get_time(cls) -> str:
        """
        计算当前时间
        :return:
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_today(cls):
        """获取今日0点整时间"""

        _today = datetime.date.today()
        return _today

    @classmethod
    def today_date(cls):
        """获取今日0点整时间"""

        _today = datetime.date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def time_after_week(cls):
        """获取一周后12点整的时间"""

        return (datetime.date.today() + datetime.timedelta(days=+6)).strftime(
            "%Y-%m-%d"
        ) + " 00:00:00"

    @classmethod
    def host(cls, value) -> str:
        """ 获取接口域名 """
        from utils import config
        return eval(f'config.host.{value}')


if __name__ == '__main__':
    print(getattr(Context(), 'host')('lianxi_host'))
    print(Context.get_today())
    print(Context.get_time())
