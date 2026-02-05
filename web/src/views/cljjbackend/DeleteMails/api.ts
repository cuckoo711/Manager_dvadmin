import { request } from '/@/utils/service';

export async function GetServers() {
  return request({
    url: '/api/CLJJServer/get_servers/',
    method: 'get'
  });
}

export async function SearchUserInfo(server_id: string, uid: string) {
  return request({
    url: '/api/cljj/metro/search_user_info/',
    method: 'get',
    params: { server_id, uid }
  });
}

export async function DeleteMails(server_id: string, uid: string, mail_ids: string[] | string) {
  return request({
    url: '/api/cljj/metro/delete_mails/',
    method: 'post',
    data: { server_id, uid, mail_ids }
  });
}
