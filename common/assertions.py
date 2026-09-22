import traceback
#处理异常堆栈信息：
#.print_exc()---打印详细报错；trace.format_exc()---把报错信息变成字符串常量；.print_stack()---打印出当前代码执行到了哪一层
import allure
import jsonpath #从json文件里直接提取数据
"""
jsonpath：这是一个专门用来在 JSON 数据里“挖宝”的库。
比如返回了多层嵌套的 {"data": {"list": [{"id":1}]}}，用 jsonpath 写 $..id 就能直接把 1 掏出来，
不用写一堆 response['data']['list'][0]['id']。
"""
import operator #运算符工具

from common.recordlog import logs
from common.connection import ConnectMysql

class Assertions:
    """
    接口断言模式，支持
    1）响应文本字符串包含模式断言
    2）响应结果相等断言
    3）响应结果不相等断言
    4）响应结果结果任意值断言
    5）数据库断言
    """

    def contains_assert(self,value,response,status_code):
        """
        字符串包含断言模式，断言预期结果的字符串是否包含在接口的响应信息里---包含即可（in）
        :param value: 预期结果，yaml文件的预期结果值
        :param response: 接口实际响应结果
        :param status_code: 响应状态码
        :return:
        """
        #断言状态标识，0成功，其他失败
        flag=0
        for assert_key,assert_value in value.items(): #.items()--视图（View）对象的形式，返回字典中所有的键值对（key-value pair）
            if assert_key =='status_code':
                if assert_value !=status_code:
                    flag +=1
                    allure.attach(
                        f"预期结果：{assert_value}\n实际结果：{status_code}",
                        '响应代码断言结果：失败',
                        attachment_type=allure.attachment_type.TEXT,
                    ) #记到报告里
                    logs.error("contains断言失败：接口返回码【%s】不等于【%s】"%(status_code,assert_value))
            else:
                resp_list=jsonpath.jsonpath(response,"$..%s"%assert_key)
                #$..---全局搜索；在response里面找
                #去接口返回的 response 里，不管 assert_key（比如 error_code）藏在哪一层，把它所有出现过的值都挖出来，装进一个叫 resp_list 的列表里
                if not resp_list:
                    flag+=1
                    logs.error(f"响应文本断言失败：接口响应中不存在字段【{assert_key}】，实际响应：{response}")
                    allure.attach(f"预期字段{assert_key}，实际响应{response}", '响应文本断言结果：失败',
                                  attachment_type=allure.attachment_type.TEXT)
                    continue
                if isinstance(resp_list[0],str): #若列表第一个值是字符串
                    resp_list=''.join(resp_list) #则把列表拼接成字符串
                if resp_list:
                    assert_value=None if assert_value.upper()=='NONE' else assert_value #如果预期结果是NONE，转化为None
                    if assert_value in resp_list:
                        logs.info("字符串包含断言成功：预期结果【%s】，实际结果【%s】"%(assert_value,resp_list))
                    else:
                        flag +=1
                        allure.attach(f"预期结果{assert_value}，实际结果{resp_list}",'响应文本断言结果：失败',attachment_type=allure.attachment_type.TEXT)
                        logs.error("响应文本断言失败：预期结果【%s】，实际结果【%s】"%(assert_value,resp_list))
        return flag

    def equal_assert(self,expected_results,actual_results,status_code=None):
        """
        相等断言模式---eq
        :param expected_results: 预期结果，yaml文件里的validation值
        :param actual_results: 接口实际响应结果
        :param status_code:
        :return:
        """
        flag=0
        if isinstance(actual_results,dict) and isinstance(expected_results,dict):
            common_keys=expected_results.keys()&actual_results.keys()
            #&---按位与，取交集，返回的是集合
            if not common_keys:
                flag+=1
                logs.error(f"相等断言失败，预期字段{list(expected_results.keys())}在接口响应中不存在，实际响应:{actual_results}")
                allure.attach(f"预期结果：{expected_results}\n实际结果：{actual_results}",'相等断言结果：失败',attachment_type=allure.attachment_type.TEXT)
                return flag
            common_key=list(common_keys)[0]
            new_actual_results={common_key:actual_results[common_key]}
            eq_assert=operator.eq(new_actual_results,expected_results)
            if eq_assert:
                logs.info(f"相等断言成功：接口实际结果：{new_actual_results}，等于预期结果：{expected_results}")
                allure.attach(f"预期结果：{new_actual_results}\n实际结果：{expected_results}",'相等断言结果：成功',attachment_type=allure.attachment_type.TEXT)
            else:
                flag+=1
                logs.error(f"相等断言失败：接口实际结果：{new_actual_results}，不等于预期结果：{expected_results}")
                allure.attach(f"预期结果：{new_actual_results}\n实际结果：{expected_results}", '相等断言结果：失败',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('相等断言--类型错误，预期结果和接口实际响应结果必须为字典类型')
        return flag

    def not_equal_assert(self,expected_results,actual_results,status_code=None):
        """
        不相等断言模式---ne
        :param expected_results: 预期结果，yaml文件里的validation值
        :param actual_results: 接口实际响应结果
        :param status_code:
        :return:
        """
        flag = 0
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):
            common_keys = expected_results.keys() & actual_results.keys()
            # &---按位与，取交集，返回的是集合
            if not common_keys:
                flag+=1
                logs.error(f"不相等断言失败，预期字段{list(expected_results.keys())}在接口响应中不存在，实际响应:{actual_results}")
                allure.attach(f"预期结果：{expected_results}\n实际结果：{actual_results}",'不相等断言结果：失败',attachment_type=allure.attachment_type.TEXT)
                return flag
            common_key=list(common_keys)[0]
            new_actual_results = {common_key: actual_results[common_key]}
            eq_assert = operator.ne(new_actual_results, expected_results)
            if eq_assert:
                logs.info(f"不相等断言成功：接口实际结果：{new_actual_results}，不等于预期结果：{expected_results}")
                allure.attach(f"预期结果：{new_actual_results}\n实际结果：{expected_results}", '不相等断言结果：成功',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1
                logs.error(f"不相等断言失败：接口实际结果：{new_actual_results}，等于预期结果：{expected_results}")
                allure.attach(f"预期结果：{new_actual_results}\n实际结果：{expected_results}", '相等断言结果：失败',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('不相等断言--类型错误，预期结果和接口实际响应结果必须为字典类型')
        return flag

    def assert_response_any(self,actual_results,expected_results):
        """
        断言接口相应信息中的body的任何属性值---单字段比较
        :param actual_results:
        :param expected_results:
        :return: 0表示测试通过
        """
        flag=0
        try:
            exp_key=list(expected_results.keys())[0]
            if exp_key in actual_results:
                act_value=actual_results[exp_key]
                rv_assert=operator.eq(act_value,list(expected_results.values())[0])
                if rv_assert:
                    logs.info("响应结果任意值断言成功")
                else:
                    flag+=1
                    logs.error("相应结果任意值断言失败")
        except Exception as e:
            logs.error(e)
            raise
        return flag

    # 【预留·未接线】响应时间断言：assert_result 目前未分发到它
    def assert_response_time(self,res_time,exp_time):
        """
        通过断言接口的响应时间和期望时间对比，小于期望时间则为通过
        :param res_time:
        :param exp_time:
        :return:
        """
        try:
            assert res_time<exp_time
            return True
        except Exception as e:
            logs.error('接口响应时间【%ss】大于预期时间【%ss】'%(res_time,exp_time))
            raise

    def assert_mysql_data(self,expected_results):
        """
        数据库断言
        :param expected_results: 预期结果，yaml文件的SQL语句（能查到数据即通过）
        :return:
        """
        flag=0
        try:
            conn=ConnectMysql()
            db_value=conn.query_all(expected_results) #在数据库中执行此语句，查到了则返回列表
            if db_value is not None:
                logs.info("数据库断言成功，查到数据：%s" % expected_results)
            else:
                flag+=1
                logs.error("数据库断言失败，未查到符合条件的数据：%s" % expected_results)
        except Exception as e:
            flag+=1
            logs.error("数据库断言失败，连接或查询异常：%s" % e)
        return flag

    def assert_result(self,expected,response,status_code):
        """
        断言，通过断言all_flag标记;在validation里面，默认只有一个字段
        :param expected:
        :param response:
        :param status_code:
        :return:
        """
        all_flag=0
        try:
            logs.info("yaml文件预期结果：%s"%expected)
            for yq in expected:
                for key,value in yq.items():
                    if key =='contains':
                        flag=self.contains_assert(value,response,status_code)
                        all_flag+=flag
                    elif key =='eq':
                        flag=self.equal_assert(value,response)
                        all_flag+=flag
                    elif key =='ne':
                        flag=self.not_equal_assert(value,response)
                        all_flag+=flag
                    elif key =='nv':
                        flag=self.assert_response_any(response,value)
                        all_flag+=flag
                    elif key =='db':
                        flag=self.assert_mysql_data(value)
                        all_flag+=flag
                    else:
                        logs.error("不支持此种断言方式")
        except Exception as e:
            logs.error("接口断言异常，请检查yaml预期结果值是否正确填写")
            raise e

        if all_flag ==0:
            logs.info("测试成功")
            assert True
        else:
            logs.error("测试失败")
            assert False

#validation是专门用来做断言的