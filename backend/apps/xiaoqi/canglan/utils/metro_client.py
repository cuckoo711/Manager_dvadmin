import requests
import re
from urllib.parse import urljoin
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from typing import Union, List


class MetroClient:
    def __init__(self, base_url: str = "https://cljjxiao7.jingtanggame.com", verify: Union[bool, str] = False, suppress_insecure_warnings: bool = True):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.logged_in = False
        self.verify = verify
        if self.verify is False and suppress_insecure_warnings:
            urllib3.disable_warnings(InsecureRequestWarning)

    def login(self, timeout: float = 15.0) -> bool:
        username = "xbadmin"
        password = "xbreak123!"
        url = urljoin(self.base_url + "/", "metro/login")
        payload = {"username": username, "password": password}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = self.session.post(url, data=payload, headers=headers, timeout=timeout, allow_redirects=True, verify=self.verify)
        if resp.status_code >= 400:
            self.logged_in = False
            return self.logged_in
        dash = self.session.get(urljoin(self.base_url + "/", "metro/"), timeout=timeout, allow_redirects=True, verify=self.verify)
        self.logged_in = self._contains_username(dash.text, username)
        return self.logged_in

    def _contains_username(self, html: str, username: str) -> bool:
        if not html or not username:
            return False
        pattern = re.compile(r'<span\s+class=["\']username["\']\s*>\s*' + re.escape(username) + r'\s*</span>', re.IGNORECASE)
        return bool(pattern.search(html))

    def is_authenticated(self) -> bool:
        return self.logged_in

    def get(self, path: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        return self.session.get(url, verify=self.verify, **kwargs)

    def post(self, path: str, data=None, json=None, **kwargs) -> requests.Response:
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        return self.session.post(url, data=data, json=json, verify=self.verify, **kwargs)

    def search_user(self, uid: str, timeout: float = 15.0) -> str:
        payload = {"uid": uid}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = self.post("metro/searchUser.html", data=payload, headers=headers, timeout=timeout)
        return resp.text

    def parse_search_result(self, html: str) -> dict:
        result = {
            "userinfo": {},
            "usermails": []
        }
        
        # 1. 解析 User Info (id="user")
        user_table_match = re.search(r'<table[^>]*id=["\']user["\'][^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if user_table_match:
            user_table_content = user_table_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', user_table_content, re.DOTALL | re.IGNORECASE)
            for row in rows:
                cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                if len(cols) >= 2:
                    key = re.sub(r'<[^>]+>', '', cols[0]).strip()
                    val = re.sub(r'<[^>]+>', '', cols[1]).strip()
                    if "用户id" in key:
                        result["userinfo"]["userid"] = val
                    elif "用户名" in key:
                        result["userinfo"]["username"] = val

        # 2. 解析 User Mails (id="usermail")
        # 尝试找到 id="usermail" 的 table，如果找不到则在整个 HTML 中搜索符合特征的行
        mail_table_match = re.search(r'<table[^>]*id=["\']usermail["\'][^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        content_to_search = mail_table_match.group(1) if mail_table_match else html
        
        # 查找所有行
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content_to_search, re.DOTALL | re.IGNORECASE)
        for row in rows:
            # 过滤掉不包含邮件 checkbox 的行
            if 'name="mail"' not in row and "name='mail'" not in row:
                continue
                
            cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            # 根据用户提供的 HTML 结构，第一列是 checkbox，后面是数据
            # <tr>
            #   <td><input type="checkbox" name="mail" value='...'/></td>
            #   <td>1767665840.0</td> (Mail ID)
            #   <td>1</td> (Type)
            #   ...
            if len(cols) >= 6:
                # 提取纯文本的辅助函数
                def clean_text(s):
                    return re.sub(r'<[^>]+>', '', s).strip()
                
                # 根据用户提供的结构定义：
                # mail = [mail_type, msg_type, item_list, source_type, 1, limit_type, is_locked, mail_ext_data]
                # 0: mail_type (是否为永久邮件)
                # 1: msg_type (邮件标题正文副标题)
                # 2: item_list (附件道具列表)
                # 3: source_type (来源类型)
                # 4: is_new (是否新邮件, 固定为1?)
                # 5: limit_type (获取限制)
                # 6: is_locked (是否锁定)
                # 7: mail_ext_data (附加数据)
                
                # cols[0] 是 checkbox
                # cols[1] 是 mail_id
                
                mail_item = {
                    "mail_id": clean_text(cols[1]),
                    "mail_type": clean_text(cols[2]),  # 0: 永久/限时
                    "msg_type": clean_text(cols[3]),   # 1: 消息类型
                    "item_list": clean_text(cols[4]),  # 2: 附件
                }
                
                # 映射后续字段
                if len(cols) > 5: mail_item["source_type"] = clean_text(cols[5]) # 3: 来源类型
                if len(cols) > 6: mail_item["is_new"] = clean_text(cols[6])      # 4: 是否新邮件
                if len(cols) > 7: mail_item["limit_type"] = clean_text(cols[7])  # 5: 获取限制
                if len(cols) > 8: mail_item["is_locked"] = clean_text(cols[8])   # 6: 是否锁定
                
                # 之后的字段（如果有）
                if len(cols) > 9: mail_item["extra"] = clean_text(cols[9])
                if len(cols) > 10: mail_item["mail_ext_data"] = clean_text(cols[10]) # 7: 附加数据

                result["usermails"].append(mail_item)
                
        return result

    def delete_mails(self, uid: str, mail_ids: List[str], timeout: float = 15.0) -> str:
        # requests 库支持传入 (key, value) 的列表来处理同名参数
        payload = [("uid", uid)]
        for mid in mail_ids:
            if mid:
                payload.append(("mail", str(mid)))
                
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = self.post("metro/searchUser.html", data=payload, headers=headers, timeout=timeout)
        return resp.text

    def get_mail_backups(self, char_id: str, timeout: float = 15.0) -> str:
        """
        获取角色邮件备份信息
        URL: {base_url}/admin/gameConfManage/mailbackups/?user_id={char_id}
        """
        resp = self.get("admin/gameConfManage/mailbackups/", params={"user_id": char_id}, timeout=timeout)
        return resp.text

    def parse_mail_backups(self, html: str) -> List[dict]:
        results = []
        table_match = re.search(r'<table[^>]*id=["\']result_list["\'][^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            return results
            
        content = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL | re.IGNORECASE)
        
        for row in rows:
            # Skip header row (thead usually has th, but tbody rows have td/th with specific classes)
            if 'class="action-checkbox"' not in row:
                continue
                
            item = {}
            
            # 1. Backup ID (from checkbox value)
            backup_id_match = re.search(r'class=["\']action-checkbox["\'][^>]*>.*?value=["\'](\d+)["\']', row, re.DOTALL | re.IGNORECASE)
            if backup_id_match:
                item["backup_id"] = backup_id_match.group(1)
            
            # 2. User ID
            user_id_match = re.search(r'class=["\']field-user_id["\'][^>]*>.*?<a[^>]*>(.*?)</a>', row, re.DOTALL | re.IGNORECASE)
            if user_id_match:
                item["user_id"] = user_id_match.group(1).strip()
                
            # 3. Mail ID
            mail_id_match = re.search(r'class=["\']field-mail_id["\'][^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            if mail_id_match:
                item["mail_id"] = mail_id_match.group(1).strip()
                
            # 4. Mail Info
            mail_info_match = re.search(r'class=["\']field-mail_info["\'][^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            if mail_info_match:
                raw_info = mail_info_match.group(1).strip()
                try:
                    # Try to parse as JSON, replacing single quotes with double quotes if necessary for standard JSON
                    # But the example shows standard JSON-like structure.
                    # If it's python string representation, json.loads might fail on None/True/False or single quotes.
                    # Given the example `[1, 8, [], 1, 0, 0, 0, {}]`, it is valid JSON.
                    item["mail_info"] = json.loads(raw_info)
                except json.JSONDecodeError:
                    item["mail_info"] = raw_info
            
            # 5. Delete Time
            add_time_match = re.search(r'class=["\']field-add_time[^"\']*["\'][^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            if add_time_match:
                item["delete_time"] = add_time_match.group(1).strip()
                
            if item:
                results.append(item)
                
        return results

    def send_recharge(self, user_ids: List[str], store_id: Union[str, int], timeout: float = 20.0) -> dict:
        users_str = ",".join([str(u).strip() for u in user_ids if str(u).strip()])
        payload = {"type": "send_recharge", "store_id": str(store_id), "user_ids": users_str}
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        resp = self.post("post/", data=payload, headers=headers, timeout=timeout, allow_redirects=True)
        try:
            data = resp.json()
        except Exception:
            txt = getattr(resp, "text", "")
            data = json.loads(txt)
        self._validate_recharge_response(data, users_str)
        return data

    def _validate_recharge_response(self, data: dict, users_str: str) -> None:
        if not isinstance(data, dict):
            raise ValueError("invalid response")
        if str(data.get("state")).lower() != "true":
            raise ValueError("recharge failed")
        msg = str(data.get("data", ""))
        norm = re.sub(r"\s+", "", msg)
        expect_users = re.sub(r"\s+", "", users_str)
        if "充值发放完毕,成功发送给：" not in msg or "失败发送的id:" not in msg:
            raise ValueError("unexpected response content")
        if expect_users not in norm:
            raise ValueError("user ids mismatch in response")

    def get_csrftoken(self) -> Union[str, None]:
        """
        获取当前的 csrftoken
        """
        return self.session.cookies.get("csrftoken")

    def recover_mail_backups(self, user_id: str, backup_ids: List[str], timeout: float = 15.0) -> str:
        """
        恢复邮件备份
        :param user_id: 玩家ID
        :param backup_ids: 备份记录ID列表 (_selected_action)
        :param timeout: 超时时间
        """
        # 1. Ensure we have a CSRF token
        token = self.get_csrftoken()
        if not token:
            # Trigger cookie set by visiting the page
            self.get_mail_backups(user_id)
            token = self.get_csrftoken()
        
        if not token:
             raise ValueError("Failed to obtain CSRF token")

        # 2. Construct Payload
        # Support multiple _selected_action parameters like delete_mails
        payload = [
            ("csrfmiddlewaretoken", token),
            ("action", "create_conf"),
            ("select_across", "0"),
            ("index", "0")
        ]
        
        for bid in backup_ids:
            if bid:
                payload.append(("_selected_action", str(bid)))
        
        # 3. Send POST request
        # URL: admin/gameConfManage/mailbackups/?q=&user_id={user_id}
        path = "admin/gameConfManage/mailbackups/"
        params = {"q": "", "user_id": user_id}
        
        # Django admin often requires Referer header
        headers = {
            "Referer": urljoin(self.base_url + "/", path) + f"?q=&user_id={user_id}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        resp = self.post(path, data=payload, params=params, headers=headers, timeout=timeout)
        return resp.text

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
