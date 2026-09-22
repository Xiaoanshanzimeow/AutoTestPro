"""单接口，一次测一个用例"""
import json
import re
from json.decoder import JSONDecodeError

import allure
import jsonpath

from common.assertions import Assertions
from common.debugtalk import DebugTalk
from common.readyaml import ReadYamlData
from common.recordlog import logs
from common.sendrequest import SendRequest
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH

class RequestBase:
    def __init__(self):
        self.run=SendRequest()
        self.conf=OperationConfig()
        self.read=ReadYamlData()
        self.asserts=Assertions()

    def replace_load(self,data):
        str_data=data
        if not isinstance(str_data,str):
            str_data=json.dumps(data,ensure_ascii=False)
        # 正则一次性匹配所有 ${...}，替代原 str.index('$') 解析：
        # 原写法会被字符串里的普通 $ 干扰、也无法处理嵌套占位符
        pattern = re.compile(r'\$\{([^{}]*)\}')
        #( )：捕获组。只有被括号包起来的内容才会被 match.group(1) 提取出来；[^{}]：定义了一个否定字符类。意思是匹配 “除了 { 和 } 之外” 的任意字符。
        def _sub(match):
            ref_all_params = match.group(1)  # 占位符内部，如 "get_extract_data(orderNumber)"
            func_name = ref_all_params[:ref_all_params.index('(')]
            func_params = ref_all_params[ref_all_params.index('(')+1:ref_all_params.index(')')]
            extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else '')
            if extract_data and isinstance(extract_data, list):
                extract_data = ','.join(extract_data)
            return str(extract_data)
        str_data = pattern.sub(_sub, str_data) #pattern.sub(替换规则, 目标字符串)



        if data and isinstance(data,dict):
            data=json.loads(str_data)
        else:
            data=str_data

        return data

    def specification_yaml(self,base_info,test_case):
        test_case=test_case.copy()
        try:
            params_type=['json','data','params']
            url_host=self.conf.get_section_for_data("api_envi",'host')
            api_name=base_info['api_name']
            allure.attach(api_name,f'接口名称：{api_name}',allure.attachment_type.TEXT)
            url=url_host+base_info['url']
            allure.attach(url,f'接口地址：{url}',allure.attachment_type.TEXT)
            method=base_info['method']
            allure.attach(method, f'请求方法：{method}', allure.attachment_type.TEXT)
            header=self.replace_load(base_info['header'])
            allure.attach(str(header), f'请求头：{header}', allure.attachment_type.TEXT)
            cookie=None
            if base_info.get('cookies') is not None:
                cookie=self.replace_load(base_info['cookies'])
            case_name=test_case.pop('case_name')
            allure.attach(case_name, f'测试用例名称：{case_name}', allure.attachment_type.TEXT)
            val=self.replace_load(test_case['validation'])
            test_case['validation']=val
            validation=json.loads(test_case.pop('validation'))
            extract=test_case.pop('extract',None)
            extract_list=test_case.pop('extract_list',None)
            for key,value in test_case.items():
                if key in params_type:
                    test_case[key]=self.replace_load(value)

            file,files=test_case.pop('files',None),None
            if file is not None:
                for fk,fv in file.items():
                    allure.attach(json.dumps(file),'导入文件')
                    files={fk:open(fv,mode='rb')}
            res=self.run.run_main(
                name=api_name,
                url=url,
                case_name=case_name,
                header=header,
                method=method,
                cookies=cookie,
                file=files,
                **test_case
            )

            status_code=res.status_code
            allure.attach(self.allure_attach_response(res.json()),'接口响应信息',attachment_type=allure.attachment_type.TEXT)
            try:
                res_json=json.loads(res.text)
                if extract is not None:
                    self.extract_data(extract,res.text)
                if extract_list is not None:
                    self.extract_data_list(extract_list,res.text)
                self.asserts.assert_result(validation,res_json,status_code)
            except JSONDecodeError as jd:
                logs.error('系统异常或接口未请求')
                raise jd
            except Exception as e:
                logs.error(e)
                raise e

        except Exception as e:
            raise e

        
    @classmethod
    def allure_attach_response(cls, response):
        if isinstance(response, dict):
            allure_response = json.dumps(response, ensure_ascii=False, indent=4)
        else:
            allure_response = response
        return allure_response

    def extract_data(self, testcase_extract, response):
        """
        提取接口的返回值，支持正则表达式和json提取器
        :param testcase_extract: testcase文件yaml中的extract值
        :param response: 接口的实际返回值
        :return:
        """
        try:
            pattern_lst = ['(.*?)', '(.+?)', r'(\d)', r'(\d*)']
            for key, value in testcase_extract.items():

                # 处理正则表达式提取
                for pat in pattern_lst:
                    if pat in value:
                        ext_lst = re.search(value, response)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_data = {key: int(ext_lst.group(1))}
                        else:
                            extract_data = {key: ext_lst.group(1)}
                        self.read.write_yaml_data(extract_data)
                # 处理json提取参数
                if '$' in value:
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    if ext_json:
                        extract_data = {key: ext_json}
                        logs.info('提取接口的返回值：', extract_data)
                    else:
                        extract_data = {key: '未提取到数据，请检查接口返回值是否为空！'}
                    self.read.write_yaml_data(extract_data)
        except Exception as e:
            logs.error(e)

    def extract_data_list(self, testcase_extract_list, response):
        """
        提取多个参数，支持正则表达式和json提取，提取结果以列表形式返回
        :param testcase_extract_list: yaml文件中的extract_list信息
        :param response: 接口的实际返回值,str类型
        :return:
        """
        try:
            for key, value in testcase_extract_list.items():
                if "(.+?)" in value or "(.*?)" in value:
                    ext_list = re.findall(value, response, re.S)
                    if ext_list:
                        extract_date = {key: ext_list}
                        logs.info('正则提取到的参数：%s' % extract_date)
                        self.read.write_yaml_data(extract_date)
                if "$" in value:
                    # 增加提取判断，有些返回结果为空提取不到，给一个默认值
                    ext_json = jsonpath.jsonpath(json.loads(response), value)
                    if ext_json:
                        extract_date = {key: ext_json}
                    else:
                        extract_date = {key: "未提取到数据，该接口返回结果可能为空"}
                    logs.info('json提取到参数：%s' % extract_date)
                    self.read.write_yaml_data(extract_date)
        except:
            logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')
"""
关键：get_testcase_yaml 返回了两种不同形状

  单接口 yaml（addUser.yaml）—— 1 个 baseInfo + N 个 testCase

  - baseInfo: {api_name: 新增用户, url: /dar/user/addUser}
    testCase:
      - case_name: 正常新增用户      # 第1个用例
      - case_name: 缺token          # 第2个用例
      - case_name: 缺username       # 第3个用例
      - case_name: 缺role_id        # 第4个用例

  get_testcase_yaml 处理它（len(data)==1，走拆开分支）：

  if len(data) <= 1:
      base_info = data[0].get('baseInfo')      # 把 baseInfo 拎出来
      for ts in data[0].get('testCase'):       # 遍历 4 个用例
          testcase_list.append([base_info, ts]) # 每个用例配一份 baseInfo
      return testcase_list

  返回的是 [baseInfo, 用例] 这样的二元组列表：
  [ [baseInfo, 用例1], [baseInfo, 用例2], [baseInfo, 用例3], [baseInfo, 用例4] ]

  pytest 参数化把它拆成两个参数：
  @pytest.mark.parametrize('base_info,testcase', ...)  # 两个名字
  def test_add_user(self, base_info, testcase):        # 两个参数
      RequestBase().specification_yaml(base_info, testcase)  # ← 所以传两个

  业务 yaml（BusinessScenario.yml）—— N 个 baseInfo 块

  - baseInfo: {api_name: 商品列表}
    testCase: [用例1]
  - baseInfo: {api_name: 商品详情}
    testCase: [用例1]
  - baseInfo: {api_name: 提交订单}
    testCase: [用例1]
  ... (5 个块)

  get_testcase_yaml 处理它（len(data)==5 > 1，走原样返回分支）：

  else:
      return data   # 直接返回 5 个块，不拆

  返回的是 5 个完整的 dict（每个含 baseInfo + testCase）：
  [ {baseInfo, testCase}, {baseInfo, testCase}, ... ]

  pytest 参数化把整个 dict 当一个参数传：
  @pytest.mark.parametrize('case_info', ...)  # 一个名字
  def test_business_scenario(self, case_info):  # 一个参数
      RequestBase().specification_yaml(case_info)  # ← 所以传一个

  所以根因是

  不是"单接口 vs 业务"决定了签名，而是 get_testcase_yaml 里那个 if len(data) <= 1
  分支，把同一个函数变成了"两种返回形状"：

  ┌─────────────────────────┬────────────────────────────────┬────────────────────────────────┐
  │                         │             单接口              │              业务              │
  ├─────────────────────────┼────────────────────────────────┼────────────────────────────────┤
  │ yaml 结构                │ 1 个 baseInfo + N 个 testCase   │ N 个 baseInfo 块               │
  ├─────────────────────────┼────────────────────────────────┼────────────────────────────────┤
  │ get_testcase_yaml 返回   │ [baseInfo, 用例] 拆开的二元组     │ 整个 {baseInfo, testCase} dict │
  ├─────────────────────────┼────────────────────────────────┼────────────────────────────────┤
  │ pytest 拆包              │ 拆成 base_info + testcase 两个   │ 整个 dict 当 case_info 一个    │
  ├─────────────────────────┼────────────────────────────────┼────────────────────────────────┤
  │ specification_yaml 签名  │ 2 个参数                        │ 1 个参数                       │
  └─────────────────────────┴────────────────────────────────┴────────────────────────────────┘

  一句话总结

  specification_yaml 之所以一个传 2 个、一个传 1 个，是因为上游 get_testcase_yaml 给它们喂的东西不一样：

  - 单接口：get_testcase_yaml 把 baseInfo 和 testCase 拆开了，所以方法要分开接 base_info 和 test_case。
  - 业务：get_testcase_yaml 把整块 {baseInfo, testCase} 原样返回，所以方法只接一个 case_info，然后自己内部
    case_info['baseInfo'] / case_info['testCase'] 去取。
"""