import pytest
import allure
from base.apiutil import RequestBase
from common.readyaml import get_testcase_yaml
from common.recordlog import logs
from common.connection import ConnectMysql

#对所有测试函数进行
@pytest.fixture(scope='function',autouse=True)
def start_and_end():
    logs.info('------------接口测试开始------------')
    yield
    logs.info('------------接口测试结束------------')

@pytest.fixture(scope='session',autouse=True)
@allure.story('登录')
def system_login():
    try:
        api_info=get_testcase_yaml('./data/loginName.yaml')
        RequestBase().specification_yaml(api_info[0][0],api_info[0][1])
    except Exception as e:
        logs.error(f'登录出错：{e}')
        raise

@pytest.fixture(scope='session',autouse=True)
def datadb_init():
    """
    会话级前置：清空订单表，保证每次从干净状态跑（db 断言依赖干净数据）
    【AI 修改】原为空壳 pass，现补上数据清理逻辑
    """
    try:
        ConnectMysql().delete("DELETE FROM orders")
    except Exception as e:
        logs.warning(f'订单表清理失败（若 MySQL 未启动可忽略）：{e}')
