import { request } from '/@/utils/service';

export async function SearchUserInfo(uid: string) {
  return request({
    url: '/api/canglan/metro/search_user_info/',
    method: 'get',
    params: { uid }
  });
}

export async function DeleteMails(uid: string, mail_ids: string[] | string) {
  return request({
    url: '/api/canglan/metro/delete_mails/',
    method: 'post',
    data: { uid, mail_ids }
  });
}
