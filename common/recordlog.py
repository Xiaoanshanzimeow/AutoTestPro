import sys

from conf import setting
import logging
import os
import time
from logging.handlers import RotatingFileHandler  # 按文件大小滚动备份，python库里面自带
import datetime

log_path = setting.FILE_PATH["LOG"]
if not os.path.exists(log_path):
    os.mkdir(log_path)
logfile_name = log_path + r"\test.{}.logs".format(time.strftime("%Y%m%d"))


class RecordLog:
    """日志模块"""

    def __init__(self):
        self.handle_overdue_log()

    def handle_overdue_log(self):
        """处理过期日志文件"""
        # 获取系统的当前时间
        now_time = datetime.datetime.now()
        # 日期偏移30天，最多保留30的日志文件，超过自动清理
        offset_date = datetime.timedelta(days=-30)
        # 获取前一天时间戳
        before_date = (now_time + offset_date).timestamp()
        # 找到目录下的文件
        files = os.listdir(log_path)
        for file in files:
            if os.path.splitext(file)[1]:
                filepath = log_path + "\\" + file
                file_create_time = os.path.getctime(filepath)  # 获取文件创建时间,返回时间戳
                # dateArray = datetime.datetime.fromtimestamp(file_createtime) #标准时间格式
                # print(dateArray.strftime("%Y--%m--%d %H:%M:%S"))
                if file_create_time < before_date:
                    os.remove(filepath)
                else:
                    continue

    def output_logging(self):
        """获取logger对象"""
        logger = logging.getLogger(__name__)
        # 防止重复打印日志
        if not logger.handlers:
            logger.setLevel(setting.LOG_LEVEL)
            log_format = logging.Formatter(
                '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s')
            # 日志输出到指定文件，滚动备份日志
            fh = RotatingFileHandler(filename=logfile_name, mode='a', maxBytes=5242880,
                                     backupCount=7,
                                     encoding='utf-8')  # maxBytes:控制单个日志文件的大小，单位是字节,backupCount:用于控制日志文件的数量

            fh.setLevel(setting.LOG_LEVEL)
            fh.setFormatter(log_format)
            # 将相应的handler添加在logger对象中
            logger.addHandler(fh)

            # 输出到控制台
            sh = logging.StreamHandler()
            sh.setLevel(setting.STREAM_LOG_LEVEL)
            sh.setFormatter(log_format)
            logger.addHandler(sh)
        return logger

#apilog = RecordLog 类的实例（没有 debug 方法）；logs = logging.Logger 类的实例（有 debug、info、error 等方法）
apilog = RecordLog()
logs = apilog.output_logging()

"""
总结
1.此文件运行后，会生成一个叫logs的“日志记录器”。在别的文件里只需要from common.recordlog import logs，就可以拿来用
2.这个logs可以做三件事：
1）logs.debugs("这是调试信息")
2）logs.info("程序开始运行")
3）logs.error("出错了！",exc_info=True)
3.日志会存到项目根目录/logs/下，文件名叫作test.20260819.logs（日期会每天变化）
"""