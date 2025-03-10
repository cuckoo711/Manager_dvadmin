"""
Creation Date: 2025/2/27
Creation Time: 下午9:19
Dir Path: backend/apps/jtgame/tools
Project Name: Manager_dvadmin_my
File Name: views.py
Editor: cuckoo
"""
import re
import socket

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action


class ToolsSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=['post'])
    def get_domain_ips(self, request):
        domains = request.data.get("domains", "")
        # 去除前后空格并按换行分割
        urls = domains.strip().splitlines()

        # 正则表达式匹配域名
        url_pattern = re.compile(r'https?://([a-zA-Z0-9.-]+)')

        # 存储域名和IP地址的结果
        result = []

        for url in urls:
            if not url.strip():
                result.append("")
            # 匹配域名
            match = url_pattern.search(url.strip())

            if match:
                domain = match.group(1)
                try:
                    # 获取IP地址
                    ip_address = socket.gethostbyname(domain)
                    result.append(f"{ip_address}")
                except socket.gaierror:
                    # 如果获取IP失败
                    result.append("无法解析")
            else:
                # 如果没有匹配到域名
                result.append("无效域名")

        return JsonResponse({"ips": '\n'.join(result)})
