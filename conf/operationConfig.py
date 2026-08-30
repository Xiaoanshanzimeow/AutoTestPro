"""解析.ini文件"""
import sys #负责异常报错
import traceback #把错误变成字符串写进日志文件
import configparser #解析.ini配置文件
from conf import setting #使operationConfig.py知道config.ini具体放在哪个位置
from common.recordlog import logs #导入日志记录器，出错可以记录到日志

class OperationConfig:
    """封装读取.ini配置文件模块"""

    def __init__(self,filepath=None):
        #1.决定读取文件
        if filepath is None:
            self.__filepath=setting.FILE_PATH['CONFIG']
        else:
            self.__filepath=filepath

        #2.创建读卡器并读取文件
        self.conf=configparser.ConfigParser() #创建读卡器
        try:
            self.conf.read(self.__filepath, encoding='utf-8') #真正去硬盘上把config.ini文件读进来
        except Exception as e:
            exc_type, exc_value, exc_obj = sys.exc_info() #返回“当前错误”的详细信息
            logs.error(str(traceback.print_exc(exc_obj))) #将刚才抓到的错误，转成完整报错文字，然后传递给 logs.error 写入日志文件

        #3.取出报告类型
        self.type=self.get_report_type('type')

    #4.打包获取整个章节
    def get_item_value(self,section_name):
        """
        :param section_name: 根据ini文件的头部获取全部值
        :return: 字典形式
        """
        items=self.conf.items(section_name)
        return dict(items)

    #5.最关键的取数
    #option就是.ini文件里面的key
    def get_section_for_data(self,section,option):
        """
        :param section: ini文件头部值
        :param option: 头部值下面的选项
        :return:
        """
        try:
            values=self.conf.get(section,option)#批量取数用这个value=self.get_item_value(section).get(option)
            return values #返回字符串
        except Exception as e:
            logs.error(str(traceback.format_exc()))
            return ''

    #6.动态写入配置
    def write_config_data(self,section,option_key,option_value):
        """写入数据到ini配置文件中"""
        if section not in self.conf.sections(): #self.conf.sections()返回配置文件里所有的章节名列表
            self.conf.add_section(section) #新建一个章节
            self.conf.set(section,option_key,option_value) #把键值对写入章节里
        else:
            logs.info("'%s'值已经存在，写入失败"%section)
        with open(self.__filepath,'w',encoding='utf-8') as f:
            self.conf.write(f) #把内存上的修改，真正保存到硬盘上的.ini文件里

    #7.针对各个数据库的“快捷取数方法”
    def get_section_mysql(self,option):
        return self.get_section_for_data("MYSQL",option)

    def get_section_redis(self, option):
        return self.get_section_for_data("REDIS", option)

    def get_section_clickhouse(self, option):
        return self.get_section_for_data("CLICKHOUSE", option)

    def get_section_mongodb(self, option):
        return self.get_section_for_data("MongoDB", option)

    def get_report_type(self,option):
        return self.get_section_for_data("REPORT_TYPE", option)

    def get_section_ssh(self,option):
        return self.get_section_for_data("SSH", option)

"""
总结：应用
# 创建这个“读卡器”机器
op = OperationConfig()

# 不用关心文件在哪、怎么读，直接拿数据
mysql_host = op.get_section_mysql("host")
redis_port = op.get_section_redis("port")
report_style = op.get_report_type("type")

print(mysql_host)  # 输出 *****
"""
