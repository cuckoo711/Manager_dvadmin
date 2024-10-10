"""
Creation date: 2024/7/24
Creation Time: 下午3:12
DIR PATH: backend/jtgame/tencent_docx
Project Name: Manager_dvadmin
FILE NAME: utils.py
Editor: 30386
"""
import os
import uuid
from datetime import datetime

import requests

from application import settings


def build_output_path():
    current_time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    base_output_dir = f'{settings.TEMPLATE_FILE_PATH}/{current_time_str}_{uuid.uuid4().hex.upper()}'
    output_path = os.path.abspath(base_output_dir)
    os.makedirs(output_path, exist_ok=True)
    return output_path
