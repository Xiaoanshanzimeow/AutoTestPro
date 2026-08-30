"""从csv文件中批量读取某一列的工具函数"""
import pandas as pd
from common.recordlog import logs
import traceback

def read_csv(filepath,col_name):
    """

    :param filepath: csv目录
    :param col_name:
    :return: 取值的列名
    """
    try:
        df=pd.read_csv(filepath,encoding='gbk') #读取csv文件，并把它转成一个叫DataFrame的对象
        data=df[col_name].tolist() #从数据表中把col_name那一列的所有数据取出来，转成列表
        return data
    except Exception:
        logs.errorz(traceback.format_exc())
