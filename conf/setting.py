"""配置信息"""
import logging #日志记录模块
import os #调用底层操作系统功能的方法
import sys #管理 Python 程序运行时的环境

#__file__：代表当前这个脚本文件的绝对路径
#os.path.dirname(__file__)：取当前文件的上一层目录
DIR_BASE=os.path.dirname(os.path.dirname(__file__))
#没有这行代码：Python 只认当前文件夹，找不到平级或上级的兄弟文件夹。
#有了这行代码：你把项目根目录强行塞进了 Python 的“搜索清单”里，从此项目里任何地方的模块，Python 都能顺着根目录找到。
sys.path.append(DIR_BASE)

#log日志输出级别
"""
DEBUG = 10（最细碎的调试信息）
INFO = 20（常规运行信息）
WARNING = 30（警告，程序还能跑）
ERROR = 40（错误，某个功能失败了）
CRITICAL = 50（致命错误，程序可能要崩）
"""
LOG_LEVEL=logging.DEBUG #LOG_LEVEL：通常用来控制写入日志文件（比如 app.log）的级别
STREAM_LOG_LEVEL=logging.DEBUG #STREAM_LOG_LEVEL：这里的 STREAM 指的就是控制台（终端 / Console），也就是 print 输出的地方。

"""
变量	值	含义（人话翻译）
API_TIMEOUT=60	          60（秒）	调用接口时，最长等待 60 秒。如果 60 秒内没收到响应，直接报超时失败，防止测试卡死。
SHEET_ID=0	               0	    测试数据写在 Excel 里，这里指定读第 1 个 Sheet 页（因为程序里从 0 开始数）。如果改成 1，就读第 2 页。
REPORT_TYPE='allure'	'allure'	测试跑完后生成报告的风格。allure 是最炫酷的网页报告，tm 可能是团队内部自定义的简化版报告。
dd_msg=False	       False（关闭）	是否发送钉钉机器人通知。False 表示跑完测试不往钉钉群里发消息，改成 True 就会自动@所有人发测试结果。
"""
#接口超时时间，单位/s
API_TIMEOUT=60

#excel文件的sheet页，默认读取第一个sheet页的数据，int类型，第一个sheet为0，以此类推0......9
SHEET_ID=0

#生成的测试报告类型，可以生成两个风格的报告：allure或tm
REPORT_TYPE='allure'

#是否发送钉钉消息
dd_msg=False

#文件路径
FILE_PATH={
    'CONFIG':os.path.join(DIR_BASE,'conf/config.ini'), #conf/operationConfig.py用到
    'LOG':os.path.join(DIR_BASE,'logs'), #common/recordlog.py用到
    'YAML':os.path.join(DIR_BASE),
    'TEMP':os.path.join(DIR_BASE,'report/temp'),
    'TMR':os.path.join(DIR_BASE,'report/tmreport'),
    'EXTRACT':os.path.join(DIR_BASE,'extract.yaml'),
    'XML':os.path.join(DIR_BASE,'data/sql'),
    'RESULTXML':os.path.join(DIR_BASE,'report'),
    'EXCEL':os.path.join(DIR_BASE,'data','测试数据.xls')
}

#默认请求头信息
LOGIN_HEADER={
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept':'application/json,text/plain,*/*',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Connection':'keep-alive',
}