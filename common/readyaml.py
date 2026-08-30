import yaml
import traceback
import os

from common.recordlog import logs
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH

#翻译yaml文件
def get_testcase_yaml(file): #传入yaml文件名
    testcase_list=[]
    try:
        with open(file,'r',encoding='utf-8') as f:
            data=yaml.safe_load(f)
            if len(data) <=1:
                yam_data=data[0]
                base_info=yam_data.get('baseInfo')
                for ts in yam_data.get('testCase'):
                    param=[base_info,ts] #把不变的base_info和会变化可能有多个的testcase分离
                    testcase_list.append(param)
                return testcase_list
            else:
                return data
    except UnicodeDecodeError:
        logs.error(f"[{file}]文件编码格式错误，--尝试使用utf-8编码解码YAML文件时发生了错误，请确保你的yaml文件是UTF-8格式！")
    except FileNotFoundError:
        logs.error(f'[{file}]文件未找到，请检查路径是否正确')
    except Exception as e:
        logs.error(f'获取[{file}]文件数据时出现未知错误：{str(e)}')


class ReadYamlData:
    """读写接口的YAML格式测试数据"""
    def __init__(self,yaml_file=None):
        if yaml_file is not None:
            self.yaml_file=yaml_file
        else:
            pass
        self.conf=OperationConfig() #造了一台配置读取器
        self.yaml_data=None

    @property #把方法当成属性调用，不用加括号
    def get_yaml_data(self):
        """
        获取测试用例yaml数据
        :param file:YAML文件
        :return: 返回list
        """
        try:
            with open(self.yaml_file,'r',encoding='utf-8') as f:
                self.yaml_data=yaml.safe_load(f)
                return self.yaml_data
        except Exception:
            logs.error(str(traceback.format_exc())) #把完整的报错堆栈（红色报错文字）转成字符串，写进日志文件里

    def write_yaml_data(self,value):
        """
        写入数据需为dict，allow_unicode=True表示写入中文，sort_keys按顺序写入
        写入YAML文件数据,主要用于接口关联
        这个方法专门往 extract.yaml（全局变量缓存池）里追加数据
        :param value: 写入数据，必须用dict
        :return:
        """
        file=None
        file_path=FILE_PATH['EXTRACT']
        """
        os.path.dirname(file_path)：获取文件所在的文件夹路径（比如 D:/project）。
        os.makedirs(..., exist_ok=True)：如果这个文件夹不存在，就自动创建；如果存在，就不报错（exist_ok=True）。这保证了写文件时不会因为目录不存在而崩溃
        """
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        try:
            file=open(file_path,'a',encoding='utf-8') #以追加（'a'）模式打开文件。追加模式的意思是：在文件末尾新增内容，不会覆盖原有的老数据
            if isinstance(value,dict):
                write_data=yaml.dump(value,allow_unicode=True,sort_keys=False) #把 Python 字典转回 YAML 格式的字符串。
                file.write(write_data)
            else:
                logs.info('写入extract.yaml文件的数据必须为字典类型')
        except Exception:
            logs.error(str(traceback.format_exc()))
        if file: #如果文件对象存在
            file.close()

    def clear_yaml_data(self):
        """
            清空extract.yaml文件数据
            :param filename: yaml文件名
            :return:
        """
        with open(FILE_PATH['EXTRACT'],'w') as f:
            f.truncate() #把文件截断到 0 字节（即清空所有内容）

    def get_extract_yaml(self,node_name,second_node_name=None): #要取的一级键名，要取的二级键名
        """
        用于读取接口提取的变量值
        :param node_name:
        :param second_node_name:
        :return:
        """
        if os.path.exists(FILE_PATH['EXTRACT']):
            pass
        else:
            logs.error('extract.yaml不存在')
            file=open(FILE_PATH['EXTRACT'],'w')
            file.close()
            logs.info('extract.yaml创建成功')
        try:
            with open(FILE_PATH['EXTRACT'],'r',encoding='utf-8') as rf:
                ext_data=yaml.safe_load(rf)
                if second_node_name is not None:
                    return ext_data[node_name]
                else:
                    return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"[extract.yaml]没有找到：{node_name},--%s"%e)

    def get_testCase_baseInfo(self,case_info):
        """
        获取testcase yaml文件的baseInfo数据
        :param case_info: yaml数据，dict类型
        :return:
        """
        pass

    def get_method(self):
        yal_data=self.get_yaml_data()
        metd=yal_data[0].get('method')
        return metd

    def get_request_parame(self):
        """
        获取yaml测试数据中的请求参数
        :return:
        """
        data_list=[]
        yaml_data=self.get_yaml_data()
        del yaml_data[0]
        for da in yaml_data:
            data_list.append(da)
        return data_list
