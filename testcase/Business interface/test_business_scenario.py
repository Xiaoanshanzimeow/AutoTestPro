import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil_business import RequestBase
from base.generateId import m_id,c_id

@allure.feature(next(m_id)+'电子商务管理系统（业务场景）') #类装饰器，类被定义，只运行1次
class TestBusinessScenario:

    @allure.story(next(c_id)+'商品列表到下单支付流程')
    @pytest.mark.parametrize(
        "case_info",
        get_testcase_yaml('./testcase/Business interface/BusinessScenario.yaml')
    )
    def test_business_scenario(self,case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)
        # get_testcase_yaml把测试用例逐个拆分，形成测试用例列表，给每一个元素都分配test_business_scenario方法，
        """
        类的大标题 (Feature)	    @allure.feature(...)        写在类上	    报告左侧边栏 "Features" 分组目录	    类加载时固定，所有用例共用
        元素的共同标题 (Story)	    @allure.story(...)          写在方法上	点开 Feature 后的 "Stories" 子分组	    方法加载时固定，所有参数化副本共用
        各自独立的标题 (Title)	    allure.dynamic.title(...)   写在方法内部	测试用例列表中的 "名称" 那一列	        运行时动态设置，每条用例都不一样
        """


"""
第二个用例（Business interface/BusinessScenario.yml）
函数走的分支：len(data) > 1（返回原始的 data）
返回值结构：[case_obj1, case_obj2, ...]（列表中的每个元素就是一个完整的字典对象，里面已经包含了 baseInfo 和所有测试步骤）
装饰器写法：@pytest.mark.parametrize("case_info", ...)
这里只写了一个变量名。pytest 会将返回列表中每一个完整对象，依次整体赋值给 case_info。
函数签名：def test_business_scenario(self, case_info)
只接收一个整体对象。你看函数内部是 case_info['baseInfo']，说明该对象内部已经自带了所有层级数据，不需要再从外部传入独立的 base_info。

业务场景测试：YAML 顶层是多个独立的场景（比如场景A、场景B），
每个场景都有自己独立的 baseInfo 和流程。此时不适合把 A 的公共信息强加给 B，所以函数保持原样返回，让测试方法自己去取内部的 baseInfo。
"""

"""
1.测试用例的结构化分类和展示

@allure.epic: 最高层级，代表一个大的产品线或业务领域。
@allure.feature: 中间层级，代表Epic下的一个具体功能模块。
@allure.story: 最细粒度，代表Feature下的一个具体用户场景或测试点

next(m_id)---测试模块标号
''---测试模块标题


2.参数化处理：
@pytesy.mark.parametrize("a",[...])
def hanshu(a)

3.动态生成标题
@allure.dynamic.title(a)
"""