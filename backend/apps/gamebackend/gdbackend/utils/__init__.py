import importlib
import os


def get_class_by_name(class_name):
    """
    根据类名字符串返回对应的类对象。

    :param class_name: 类名字符串
    :return: 对应的类对象，找不到时返回 None
    """
    current_dir = os.path.dirname(__file__)
    for file in os.listdir(current_dir):
        if file.endswith(".py") and file != "__init__.py":
            module_name = file[:-3]  # 去掉 .py 后缀
            try:
                # 动态导入模块
                module = importlib.import_module(f".{module_name}", package=__name__)
                # 遍历模块内的属性
                if hasattr(module, class_name):
                    return getattr(module, class_name)
            except ImportError:
                pass
    return None
