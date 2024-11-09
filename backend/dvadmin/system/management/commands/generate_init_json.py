import json
import logging
import os

import django
from django.db.models import QuerySet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()
from django.core.management.base import BaseCommand

from application.settings import BASE_DIR
from dvadmin.system.models import Menu, Users, Dept, Role, ApiWhiteList, Dictionary, SystemConfig
from dvadmin.system.fixtures.initSerializer import UsersInitSerializer, DeptInitSerializer, RoleInitSerializer, \
    MenuInitSerializer, ApiWhiteListInitSerializer, DictionaryInitSerializer, SystemConfigInitSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    生产初始化菜单: python manage.py generate_init_json 生成初始化的model名
    例如：
    全部生成：python manage.py generate_init_json
    只生成某个model的： python manage.py generate_init_json users
    """

    @staticmethod
    def serializer_data(serializer, query_set: QuerySet, output_dir: str):
        # 创建输出目录（如果不存在）
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        serializer = serializer(query_set, many=True)
        data = json.loads(json.dumps(serializer.data, ensure_ascii=False))
        file_path = os.path.join(output_dir, f'init_{query_set.model._meta.model_name}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return

    def add_arguments(self, parser):
        parser.add_argument("generate_name", nargs="*", type=str, help="初始化生成的表名")
        parser.add_argument("-O", "--output_dir", type=str, default=os.path.join(BASE_DIR, 'init_fixtures'),
                            help="指定输出文件夹路径")
        parser.add_argument("-C", "--compare", type=str, nargs="?",
                            const=os.path.join(BASE_DIR, 'dvadmin/system/fixtures'),
                            help="比较模式，接受一个路径，默认路径为根目录下'dvadmin/system/fixtures'")
        parser.add_argument("-V", "--verbose", action="store_true", help="显示详细信息")

    def generate_users(self, output_dir):
        self.serializer_data(UsersInitSerializer, Users.objects.all(), output_dir)

    def generate_role(self, output_dir):
        self.serializer_data(RoleInitSerializer, Role.objects.all(), output_dir)

    def generate_dept(self, output_dir):
        self.serializer_data(DeptInitSerializer, Dept.objects.filter(parent_id__isnull=True), output_dir)

    def generate_menu(self, output_dir):
        self.serializer_data(MenuInitSerializer, Menu.objects.filter(parent_id__isnull=True), output_dir)

    def generate_api_white_list(self, output_dir):
        self.serializer_data(ApiWhiteListInitSerializer, ApiWhiteList.objects.all(), output_dir)

    def generate_dictionary(self, output_dir):
        self.serializer_data(DictionaryInitSerializer, Dictionary.objects.filter(parent_id__isnull=True), output_dir)

    def generate_system_config(self, output_dir):
        self.serializer_data(SystemConfigInitSerializer, SystemConfig.objects.filter(parent_id__isnull=True),
                             output_dir)

    def handle(self, *args, **options):
        verbose = options.get('verbose')
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        generate_name = options.get('generate_name')
        output_dir = options.get('output_dir')

        generate_name_dict = {
            "users": self.generate_users,
            "role": self.generate_role,
            "dept": self.generate_dept,
            "menu": self.generate_menu,
            "api_white_list": self.generate_api_white_list,
            "dictionary": self.generate_dictionary,
            "system_config": self.generate_system_config,
        }
        if not generate_name:
            for ele in generate_name_dict.keys():
                generate_name_dict[ele](output_dir)
        else:
            for name in generate_name:
                if name not in generate_name_dict:
                    print(f"该初始化方法尚未配置\n{generate_name_dict}")
                    raise Exception(f"该初始化方法尚未配置,已配置项:{list(generate_name_dict.keys())}")
                generate_name_dict[name](output_dir)
        logger.info(f"初始化数据生成完成, 输出目录: {output_dir}")

        compare_path = options.get('compare')
        if compare_path:
            logger.info(f"比较模式，比较路径: {compare_path}")
            self._compare_data(compare_path, output_dir)

        return

    def _compare_json(self, json1, json2, path=""):
        if str(type(json1)) != str(type(json2)):
            print(f"类型不匹配: {path} | {type(json1)} != {type(json2)}")
            return

        if isinstance(json1, dict):
            for key in json1.keys() | json2.keys():
                new_path = f"{path}/{key}" if path else key
                if key not in json1:
                    print(f"键缺失: {new_path} 在第一个 JSON 中不存在")
                elif key not in json2:
                    print(f"键缺失: {new_path} 在第二个 JSON 中不存在")
                else:
                    self._compare_json(json1[key], json2[key], new_path)

        elif isinstance(json1, list):
            len1, len2 = len(json1), len(json2)
            if len1 != len2:
                print(f"列表长度不匹配: {path} | 长度 {len1} != {len2}")
            for index, (item1, item2) in enumerate(zip(json1, json2)):
                new_path = f"{path}[{index}]"
                self._compare_json(item1, item2, new_path)

        else:
            if json1 != json2:
                print(f"值不匹配: {path} | {json1} != {json2}")

    def _compare_data(self, compare_path, output_dir):
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json') and file.startswith('init_'):
                    if not os.path.exists(os.path.join(compare_path, file)):
                        logger.error(f"比较结果: 未找到对应的初始化数据文件--{file}")
                        continue
                    with open(os.path.join(compare_path, file), 'r', encoding='utf-8') as f:
                        compare_data = json.load(f)
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if compare_data != data:
                        logger.error(f"比较结果: 两份初始化数据内容不一致--{file}")
                        self._compare_json(compare_data, data)
                    else:
                        logger.info(f"比较结果: 两份初始化数据内容完全一致--{file}")
        return
