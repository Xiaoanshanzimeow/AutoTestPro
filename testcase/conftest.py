import pytest
import allure
from base.apiutil import RequestBase
from common.readyaml import get_testcase_yaml
from common.recordlog import logs


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
        exit()

@pytest.fixture(scope='session',autouse=True)
def datadb_init():
    """
    后置处理器，比如测试后的数据清理
    :return:
    """
    pass
