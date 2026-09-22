import json
import allure
import pytest
import requests
import urllib3
import time

from conf import setting
from common.recordlog import logs
from common.readyaml import ReadYamlData
from urllib3.exceptions import InsecureRequestWarning

class SendRequest:
    """发送接口请求，暂时只写了get和post方法的请求"""
    def __init__(self,cookie=None):
        self.cookie=cookie
        self.read=ReadYamlData()

    def get(self,url,data,header):
        """

        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return:
        """
        #忽略HTTPS证书警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response=requests.get(url=url,headers=header,cookies=self.cookie,verify=False) #忽略SSH正数警告
            else:
                response=requests.get(url=url,data=data,headers=header,cookies=self.cookie,verify=False)
        except requests.RequestException as e: #只捕获 requests 库自身抛出的异常
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None

        #响应时间/毫秒
        res_ms=response.elapsed.microseconds/1000
        #响应时间/秒
        res_second=response.elapsed.total_seconds()
        response_dict=dict() #新建一个空白字典

        #接口响应状态码
        response_dict['code']=response.status_code
        #接口响应文本
        response_dict['text']=response.text

        try:
            response_dict['body']=response.json().get('body')
        except Exception:
            response_dict['body']=''

        response_dict['res_ms']=res_ms
        response_dict['res_second']=res_second

        return response_dict

    def post(self,url,data,header):
        """

        :param url:
        :param data:
        :param header:
        :return:
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response=requests.post(url=url,headers=header,cookies=self.cookie,verify=False)
            else:
                response=requests.post(url=url,data=data,headers=header,cookies=self.cookie,verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None

        res_ms=response.elapsed.microseconds/1000
        res_second=response.elapsed.total_seconds()
        response_dict=dict()
        response_dict['code']=response.status_code
        response_dict['text']=response.text
        try:
            response_dict['body']=response.json().get('body')
        except Exception:
            response_dict['body']=''
        response_dict['res_ms']=res_ms
        response_dict['res_second']=res_second
        return response_dict

    def send_request(self,**kwargs): #参数 **kwargs 表示接收任意数量的关键字参数
        #创建session对话，自动管理cookie
        session=requests.session()
        result=None
        cookie={}
        try:
            result=session.request(**kwargs)
            #result.cookies 是 RequestsCookieJar 类型（一种特殊对象）。这行代码调用工具函数，把它转换成普通的Python字典，便于后面写入YAML文件
            set_cookie=requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie['cookie']=set_cookie
                self.read.write_yaml_data(cookie)#把cookie存到extract.yaml
                logs.info("cookies:%s"%cookie)
            logs.info("接口返回信息：%s"% result.text if result.text else result)
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError---连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致程序报错！") #强制将当前pytest测试用例标记为失败状态，并中断执行
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result

    def run_main(self,name,url,case_name,header,method,cookies=None,file=None,**kwargs):
        #**kwargs--YAML中定义的动态参数
        """
        接口请求
        :param name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例名称
        :param header: 请求头
        :param method:
        :param cookies:
        :param file: 上传文件接口
        :param kwargs: 请求参数，根据yaml文件的参数类型
        :return:
        """
        try:
            #收集报告日志
            logs.info('接口名称：%s'%name)
            logs.info('请求地址：%s'%url)
            logs.info('请求方式：%s'%method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % header)
            logs.info('Cookie：%s' % cookies)
            req_params=json.dumps(kwargs,ensure_ascii=False) #把字典转换成JSON字符串
            if 'data' in kwargs.keys(): #表单提交
                allure.attach(req_params,'请求参数',allure.attachment_type.TEXT)
                logs.info("请求参数：%s" %kwargs)
            elif 'json' in kwargs.keys(): #json提交
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif 'params' in kwargs.keys(): #URL查询参数
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)
        urllib3.disable_warnings(InsecureRequestWarning)
        response=self.send_request(
            method=method,
            url=url,
            headers=header,
            cookies=cookies,
            files=file,
            timeout=setting.API_TIMEOUT,
            verify=False,
            **kwargs)

        return response

