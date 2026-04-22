"""
检查加载的模块
"""
import sys
sys.path.insert(0, 'e:\\YOYO\\backend')

# 清除缓存，强制重新加载
if 'routers.diary' in sys.modules:
    del sys.modules['routers.diary']
if 'routers' in sys.modules:
    del sys.modules['routers']

from routers import diary

print("模块文件路径:", diary.__file__)
print()

# 读取 get_comments 函数的源代码
import inspect
source = inspect.getsource(diary.get_comments)
print("get_comments 函数源码前 800 字符:")
print(source[:800])
