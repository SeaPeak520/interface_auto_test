from typing import List, Union, Dict

import pymysql
from dbutils.pooled_db import PooledDB
from loguru import logger

from common.exceptions.exceptions import DataAcquisitionFailed, MysqlConnectionError
from models.db_model import SetupTeardownType
from utils import config


class MysqlDB:
    # 初始化
    def __init__(self):
        self._conn = self.get_mysql_conn(host=config.mysql.host,
                                         port=config.mysql.port,
                                         user=config.mysql.user,
                                         pwd=config.mysql.pwd,
                                         db=config.mysql.db
                                         )
        self._cur = self._conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 释放资源
    def __del__(self):
        try:
            # 关闭游标
            self._cur.close()
            # 关闭连接
            self._conn.close()
        except AttributeError as error:
            logger.error(f"数据库关闭失败，失败原因 {error}", )

    def get_mysql_conn(self, host: str, port: int, user: str, pwd: str, db: str):
        """
        :param host: 数据库主机
        :param port: 数据库端口
        :param user: 数据库用户
        :param pwd: 数据库密码
        :param db: 数据库名称
        :return:
        """
        try:
            return PooledDB(
                creator=pymysql,
                mincached=0,  # 最小空闲数
                maxcached=3,  # 最大空闲数
                maxshared=5,  # 池中共享连接的最大数量。默认为0，即每个连接都是专用的，不可共享(不常用，建议默认)
                maxconnections=5,  # 被允许的最大连接数。默认为0，无最大数量限制。(视情况而定)
                blocking=True,
                # 连接数达到最大时，新连接是否可阻塞。默认False，即达到最大连接数时，再取新连接将会报错。(建议True，达到最大连接数时，新连接阻塞，等待连接数减少再连接)
                maxusage=0,  # 连接的最大使用次数。默认0，即无使用次数限制。(建议默认)
                setsession=None,  # 可选的SQL命令列表，可用于准备会话。(例如设置时区)
                host=host,
                port=port,
                user=user,
                passwd=pwd,
                db=db,
                use_unicode=True,  # True显示str，False显示byte
                charset='utf8',
            ).connection()
        except MysqlConnectionError as e:
            logger.error(f"数据库连接错误: {e}")

    def query(self, sql: str, state: str = 'all') -> Union[List, Dict, int]:
        """
        :param sql: 要执行的sql
        :param state: all| one | num
        :return: List[dict,dict] [{结果1},{结果2}] | dict {'',''} | int 1
        """
        try:
            logger.info(f'查询sql语句：{sql}')
            if state == 'num':
                result = self._cur.execute(sql)
                self._conn.commit()
                logger.info(f'查询结果：{result}')
                return result
            else:
                self._cur.execute(sql)
                self._conn.commit()
                result = self._cur.fetchall() if state == 'all' else self._cur.fetchone()
                logger.info(f'查询结果：{result}')
                return result
        except AttributeError as error:
            logger.error(f"数据库连接失败，失败原因 {error}")
            raise

    def execute(self, sql: str) -> int:
        """
        :param sql: 要执行的sql
        :return: 1 (int) 插入的数量
        """
        try:
            logger.info(f'执行sql语句：{sql}')
            result = self._cur.execute(sql)
            self._conn.commit()
            logger.info(f'sql语句执行成功：{result}')
            return result
        except AttributeError as e:
            logger.error(f"数据库连接失败，失败原因: {e}")
            # 如果事务异常，则回滚数据
            self._conn.rollback()
            raise


class SqlHandler(MysqlDB):
    def sql_handler(self, sql: list) -> List:
        """
          :param sql: 要执行的sql
        """
        result = []
        for i in sql:
            _sql_type = i[:6].upper()
            if _sql_type in SetupTeardownType._member_names_:
                if _sql_type == SetupTeardownType.SELECT.value:
                    result.append(self.query(i))
                elif _sql_type == SetupTeardownType.NUM.value:
                    result.append(self.query(i,state='num'))
                else:
                    result.append(self.execute(i))
            else:
                raise DataAcquisitionFailed(f"类型不正确: {_sql_type}，应为{SetupTeardownType._member_names_}")
        return result


if __name__ == "__main__":
    # 用法

    ss_sql = ["select * from user limit 10",'select count(*) as count from user']
    # sqkl = ["select * from "]
    s = SqlHandler()
    sql_data = s.sql_handler(ss_sql)
    print(sql_data)
    print(sql_data[0])
    print(sql_data[1])
    #print(sql_data[])
    # print(sql_data)  # [{'uuid': 'a'},{'uuid': 'b'}]
    # print(sql_data[0])  # {'uuid': 'a'}
    # print(jsonpath(sql_data[0], '$.uuid'))  # ['a']
    # print(jsonpath(sql_data[0], '$.uuid')[0])  # a
