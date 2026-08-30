"""
没有 __init__.py：Python 把 testcase 文件夹当成一个普通的系统文件夹。
你在 run.py 里写 from testcase import xxx，Python 会直接报错：ModuleNotFoundError（找不到这个模块）。

有 __init__.py：Python 立刻变脸，把它当成一个“包”。这时候，你就可以用 import 语句去引用这个文件夹里的内容了。
"""