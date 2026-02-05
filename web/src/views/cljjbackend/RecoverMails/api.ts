import { request } from '/@/utils/service';

export async function GetServers() {
  return request({
    url: '/api/CLJJServer/get_servers/',
    method: 'get'
  });
}

export async function MailBackups(server_id: string, user_id: string) {
  return request({
    url: '/api/cljj/metro/mail_backups/',
    method: 'get',
    params: { server_id, user_id }
  });
}

export async function RecoverMailBackups(server_id: string, user_id: string, backup_ids: string[] | string) {
  return request({
    url: '/api/cljj/metro/recover_mail_backups/',
    method: 'post',
    data: { server_id, user_id, backup_ids }
  });
}
