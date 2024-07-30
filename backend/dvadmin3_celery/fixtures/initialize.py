# 初始化
import os

import django

from dvadmin.system.views.menu import MenuCreateSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
django.setup()


from dvadmin.utils.core_initialize import CoreInitialize


class Initialize(CoreInitialize):

    def init_menu(self):
        """
        初始化菜单信息
        """
        self.init_base(MenuCreateSerializer, unique_fields=['name', 'web_path', 'component', 'component_name'])

    def run(self):
        self.init_menu()


if __name__ == "__main__":
    Initialize(app='dvadmin3_celery').run()
