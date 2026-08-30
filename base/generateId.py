"""
定义两个生成器函数，创建对应生成器对象
测试模块和测试用例生成带有序号前缀的编号，保证allure报告中的展示顺序和pytest实际执行顺序一致
"""
def generate_module_id():
    for i in range(1.1000):
        module_id='M'+str(i).zfill(2)+'_'
        yield module_id

def generate_testcase_id():
    for i in range(1,1000):
        case_id='C'+str(i).zfill(2)+"_"
        yield case_id

m_id=generate_module_id()
c_id=generate_testcase_id()