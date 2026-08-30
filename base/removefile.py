import os
from common.recordlog import logs

def  remove_file(filepath,endlst):
    """
    删除文件
    :param filepath: 路径
    :param endlst: 删除的后缀，例如['json','txt','attach']
    :return:
    """
    try:
        if os.path.exists(filepath): #检查路（文件本身）径是否存在
            dir_lst_files=os.listdir(filepath) #获得该路径下所有文件和文件夹的名称，返回列表
            for file_name in dir_lst_files:
                fpath=filepath+'\\'+file_name
                if isinstance(endlst,list):
                    for ft in endlst:
                        if file_name.endwith(ft):
                            os.remove(fpath)
                else:
                    raise TypeError('file Type error,must be list')
        else:
            os.makedirs(filepath) #创整条路径上的文件夹
    except Exception as e:
        logs.error(e)

def remove_directory(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logs.error(e)