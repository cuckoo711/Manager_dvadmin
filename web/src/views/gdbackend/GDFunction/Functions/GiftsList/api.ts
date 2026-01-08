import {request} from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';
export const apiPrefix = '/api/GDToken/';


export function GetList(query: UserPageQuery, token: string) {
    return request({
        url: apiPrefix + token + '/get_giftslist/',
        method: 'get',
        params: query,
    });
}

export function DelObj(id: InfoReq, token: string) {
    return request({
        url: apiPrefix + token + '/del_gift/',
        method: 'get',
        params: {
            gift: id
        },
    });
}
