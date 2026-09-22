#coding:utf-8
import time
import pytest
from common.readyaml import ReadYamlData
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from conf.setting import dd_msg

import warnings

_START = time.time()

yfd=ReadYamlData()

@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    warnings.simplefilter("ignore",ResourceWarning)

    yfd.clear_yaml_data() #清空extract.yaml文件
    remove_file("./report/temp",['json','txt','attach','properties'])

#terminalreporter 是 Pytest 运行时内置的一个 TerminalReporter 对象，它负责收集和管理测试执行过程中的各项统计信息（如通过、失败、跳过等），并负责向终端输出结果
def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    # terminalreporter.stats是一个字典，键为测试结果状态，值为对应状态的测试报告对象列表
    passed = len(terminalreporter.stats.get('passed', []))  # 通过的数量
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    # 【AI 修改】xdist 下 master 进程不参与收集，_numcollected 恒为 0，
    # 改用各结果状态数量之和（通过+失败+错误+跳过=收集到的用例总数）
    total = passed + failed + error + skipped
    duration = time.time() - _START
    """
    time.time() 返回当前时间戳（浮点数，单位秒）。
    terminalreporter._sessionstarttime 是内部属性，记录了 测试会话开始的时间戳（在收集阶段之前就已设定）。
    两者相减得到从会话开始到调用该函数时的耗时，即测试执行的总时长（秒）。
    """

    summary=f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """

    print(summary)
    return summary

def pytest_terminal_summary(terminalreporter,exitstatus,config):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary=generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)