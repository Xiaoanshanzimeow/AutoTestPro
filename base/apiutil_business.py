"""取 YAML → 动态替换变量 → 发请求 → 提取返回值 → 断言"""
from common.sendrequest import SendRequest
from common.readyaml import ReadYamlData
from common.recordlog import logs
from conf.operationConfig import OperationConfig
from common.assertions import Assertions
from common.debugtalk import DebugTalk
import allure
import json
import jsonpath
import re
import traceback
from json.decoder import JSONDecodeError

assert_res=Assertions()

class RequestBase(object):
    def __init__(self):
        self.run=SendRequest()
        self.read=ReadYamlData()
        self.conf=OperationConfig()

    @staticmethod
    def handler_yaml_list(data_dict):
        """处理yaml文件测试用例请求参数为list情况，以数组形式"""
        try:
            for key,value in data_dict.items():
                if isinstance(value,list): #ids: ["1,2,3", "4,5,6"]
                    value_list=','.join(value).split(',') #["1","2","3","4","5","6"]
                    data_dict[key]=value_list
            return data_dict
        except Exception:
            logs.error(str(traceback.format_exc()))

    def replace_load(self,data):
        """yaml数据替换解析---把字符串中的${...}占位符替换成真实的数据"""
        str_data=data #传入的data可能是字符串，也可能是字典
        #后续查找替换是在字符串的基础上
        if not isinstance(data,str):
            str_data=json.dumps(data,ensure_ascii=False) #如果不是字符串，就转成json字符串
        for i in range(str_data.count("${")):
            if "${" in str_data and "}" in str_data: #检查是否还有
                #.index()---找出现的起始位置，找不到抛异常
                start_index=str_data.index("$") #占位符起始位置
                end_index=str_data.index("}",start_index) #从start_index开始找，找第一个出现的}
                #提取完整的占位符，这个字符串就是要替换的内容
                ref_all_params=str_data[start_index:end_index+1] #sl[a:b]--在sl里面截一段内容（左闭右开）
                #提取函数名,例如${get_yaml_data(name)} → 函数名是 get_yaml_data
                func_name=ref_all_params[2:ref_all_params.index("(")]
                #提取函数参数
                func_params=ref_all_params[ref_all_params.index("(")+1:ref_all_params.index(")")]
                #调用函数---python的反射机制（getattr）
                #1）getattr(对象，“方法名”)，获取该对象的上的该方法，如：getattr(DebugTalk(), "get_yaml_data") 就会拿到 get_yaml_data 这个方法
                #2）func_params.split(',')，按逗号切割参数字符串变成列表，如：func_params = "name,age" → ["name", "age"]
                #3）*把列表展开，作为多位置传参给函数
                #4）如果func_params不为空就执行，为空则传""
                """
                '分隔符'.join(list)---列表->字符串--用分隔符把序列里的元素拼接成字符串
                .split('分隔符')---字符串->列表--把字符串按分隔符号分割成一个个元素返回列表
                """
                extract_data=getattr(DebugTalk(),func_name)(*func_params.split(',') if func_params else "")
                #处理返回值为列表的情况---str.replace要求替换内容为字符串类型
                if extract_data and isinstance(extract_data,list):
                    extract_data=','.join(extract_data)
                #替换占位符---str.replace(旧内容,新内容,替换次数)
                str_data=str_data.replace(ref_all_params,str(extract_data))

        #还原数据
        #1）若最开始传入的data是字典，则要把替换后的字符串转回字典
        if data and isinstance(data,dict):
            data=json.loads(str_data)
            self.handler_yaml_list(data) #列表展平，防止yaml文件里的数据写在一起
        #2）否则返回
        else:
            data=str_data
        return data

    def specification_yaml(self,case_info):
        """
        规范yaml测试用例的写法
        :param case_info: list类型，调试取case_info[0]-->dict
        :return:
        从 YAML 配置中读取一个接口的测试定义。
        处理动态占位符（${...}）。
        遍历每一个测试用例，发送 HTTP 请求。
        记录请求和响应信息到 Allure 报告。
        执行数据提取和结果断言
        """
        params_type=['params','data','json']
        cookie=None #存放三种常见的HTTP请求参数类型：params--查询参数；data--表单数据；json--JSON数据
        try:
            #拼接url=接口基础地址+接口用例里面的地址
            base_url=self.conf.get_section_for_data('api_envi','host')
            url=base_url+case_info["baseInfo"]["url"]
            #记录地址到allure报告
            allure.attach(url,f"接口地址：{url}")
            #获取接口名称并记录
            api_name=case_info["baseInfo"]["api_name"]
            allure.attach(api_name,f"接口名：{api_name}")
            #获取请求方法并记录
            method=case_info["baseInfo"]["method"]
            allure.attach(method,f"请求方法{method}")
            #处理请求头（可能包含${}占位符
            header=self.replace_load(case_info["baseInfo"]["header"])
            allure.attach(str(header),'请求头信息',allure.attachment_type.TEXT) #指定附件类型为纯文本
            """
            allure.attach(body, name=None, attachment_type=None, extension=None)
            参数说明：
            body (必填)： 要添加的附件内容，通常是字符串或字节数据。
            name (可选)： 附件在报告中显示的文件名。
            attachment_type (可选)： 附件的MIME类型，使用 allure.attachment_type 枚举指定。
            extension (可选)： 附件保存的文件后缀名
            """
            #尝试处理cookie
            try:
                cookie=self.replace_load(case_info["baseInfo"]["cookie"])
                allure.attach(cookie,'Cookie',allure.attachment_type.TEXT)
            except:
                pass
            #遍历测试用例列表
            for tc in case_info["testCase"]:
                # 从测试用例里面取出case_name，剩下纯粹为请求参数
                case_name=tc.pop("case_name") #.pop()---删除键值对，返回value
                allure.attach(case_name,f'测试用例名称：{case_name}',allure.attachment_type.TEXT)
                #处理断言数据（可能有占位符）
                val=self.replace_load(tc.get("validation"))
                tc["validation"]=val
                #因为yaml文件里的validation指向的value很可能是字符串---s = "[{'eq': ['code', 0]}, {'eq': ['msg', 'success']}]"，需要转化成列表，逐条执行断言
                validation=eval(tc.pop("validation"))
                #去元素的value，先变成list，再变成str，最后连成list
                allure_validation=list(str(list(i.values())) for i in validation)
                allure.attach(allure_validation,"预期结果",allure.attachment_type.TEXT)
                #处理提取表达式
                extract=tc.pop('extract',None) #不存在则返回None
                extract_lst=tc.pop("extract_lst",None)

                #循环处理请求参数字段
                #遍历tc剩余键值对
                for key,value in tc.items():
                    #如果键是三种请求参数类型里面的一种
                    if key in params_type:
                        tc[key]=self.replace_load(value) #可能有占位符
                #处理文件上传
                file,files=tc.pop("file",None),None
                if file is not None:
                    for fk,fv in file.items():
                        allure.attach(json.dumps(file),'导入文件')
                        files={fk:open(fv,'rb')}
                res=self.run.run_main(
                    name=api_name,
                    url=url,
                    case_name=case_name,
                    header=header,
                    method=method,
                    cookies=None,
                    file=None,
                    **tc #**tc 将 tc 字典中剩余的键值对作为关键字参数传入
                )
                #记录响应文本和状态码
                res_text=res.text
                allure.attach(res_text,'接口相应信息',allure.attachment_type.TEXT)
                status_code=res.status_code
                allure.attach(self.allure_attach_response(res.json()),'接口响应信息',allure.attachment_type.TEXT)

                #进入第二个try快进行断言和处理
                try:
                    #json.dumps()--python对象转成json字符串；json.loads()--json字符串转成python对象；yaml.safe_load()--yaml字符串转成python字典
                    res_json=json.loads(res_text)
                    if extract is not None:
                        self.extract_data(extract,res_text)
                    if extract_lst is not None:
                        self.extract_data_lst(extract, res_text)
                    #处理断言
                    assert_res.assert_result(validation,res_json,status_code)
                except JSONDecodeError as js: #响应不是合法 JSON
                    logs.error("系统异常或者接口未请求！")
                    raise js
                except Exception as e:
                    logs.error(str(traceback.format_exc()))
                    raise e
        except Exception as e:
            logs.error(e)
            raise e

    @classmethod #类方法，可以类名调用，可以self调用
    #res.text---响应体原始文本内容；res.json()---响应体是json格式，转化为python对象
    def allure_attach_response(cls,response):
        if isinstance(response,dict):
            allure_response=json.dumps(response,ensure_asxii=False,indent=4) #转为json字符串
        else:
            allure_response=response
        return allure_response

    def extract_data(self, testcase_extract, response):
        """
        提取接口的返回参数，支持正则表达式和json提取，提取单个参数
        :param testcase_extract: testcase文件yaml中的extract值
        :param response: 接口的实际返回值,str类型
        :return:
        """
        pattern_lst = ['(.+?)', '(.*?)', r'(\d+)', r'(\d*)']
        try:
            for key, value in testcase_extract.items():
                for pat in pattern_lst:
                    if pat in value:
                        ext_list = re.search(value, response)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_date = {key: int(ext_list.group(1))}
                        else:
                            extract_date = {key: ext_list.group(1)}
                        logs.info('正则提取到的参数：%s' % extract_date)
                        self.read.write_yaml_data(extract_date)
                if "$" in value:
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    if ext_json:
                        extract_date = {key: ext_json}
                    else:
                        extract_date = {key: "未提取到数据，该接口返回结果可能为空"}
                    logs.info('json提取到参数：%s' % extract_date)
                    self.read.write_yaml_data(extract_date)
        except:
            logs.error('接口返回值提取异常，请检查yaml文件extract表达式是否正确！')

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
针对乱七八糟的json.dumps()/json.loads)_/json.safe_load()的类型转换
1.replace_load():
1.1因为获取测试用例是用common.ReadYaml里面的get_testcase_yaml()方法，其中使用了json.safe_load()，把yaml字符串转变为python对象---dict
1.2替换占位符时候，必须是str类型才可以用replace，所以先用json.dumps()转换成字符串 #39#40
1.3最后再换回原类型 #70#71
2.specification_yaml()
2.1因为replace_load()只还原字典，其余全返回字符串，，而validation的value是列表，所以用eval()强行转换回list #129
2.2res.text是字符串（服务器返回的原始文本），想要拿他断言、取值，必须先转成dict #168
"""