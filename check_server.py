"""
检查服务器环境和模块
"""
import sys
sys.path.insert(0, 'e:\\YOYO\\backend')

import os
print("当前工作目录:", os.getcwd())
print("脚本所在目录:", os.path.dirname(os.path.abspath(__file__)))
print()

# 检查 diary 模块
from routers import diary
print("diary 模块路径:", diary.__file__)
print()

# 读取 get_comments 函数的源代码
import inspect
source = inspect.getsource(diary.get_comments)
print("get_comments 函数完整源码:")
print(source)
