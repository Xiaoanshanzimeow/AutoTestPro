import logging
import os
import sys
from dotenv import load_dotenv

DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)

PROJECT_ROOT=os.path.dirname(os.path.dirname(DIR_BASE))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# log日志输出级别
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位/s
API_TIMEOUT = 60

# excel文件的sheet页，默认读取第一个sheet页的数据，int类型，第一个sheet为0，以此类推0.....9
SHEET_ID = 0

# 生成的测试报告类型，可以生成两个风格的报告，allure或tm
REPORT_TYPE = 'allure'

# 是否发送钉钉消息
dd_msg = False

# 文件路径
FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'conf/config.ini'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'),
    'TMR': os.path.join(DIR_BASE, 'report/tmreport'),
    'EXTRACT': os.path.join(DIR_BASE, 'extract.yaml'),
    'XML': os.path.join(DIR_BASE, 'data/sql'),
    'RESULTXML': os.path.join(DIR_BASE, 'report'),
    'EXCEL': os.path.join(DIR_BASE, 'data', '测试数据.xls')
}

# 默认请求头信息
LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}

# MySQL 数据库配置（mock 模拟真实后端：下单/回调时落库）
# 与 test 侧 conf/config.ini 的 [MYSQL] 保持一致，指向同一个库
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST','127.0.0.1'),
    'port': 3306,
    'user': os.getenv('DB_USER','root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE','zqsjfx'),
}
