import { request } from '/@/utils/service';

export async function MailBackups(user_id: string) {
  return request({
    url: '/api/canglan/metro/mail_backups/',
    method: 'get',
    params: { user_id }
  });
}

export async function RecoverMailBackups(user_id: string, backup_ids: string[] | string) {
  return request({
    url: '/api/canglan/metro/recover_mail_backups/',
    method: 'post',
    data: { user_id, backup_ids }
  });
}
