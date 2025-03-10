import {request} from '/@/utils/service';
import {UserPageQuery, AddReq, DelReq, EditReq, InfoReq} from '@fast-crud/fast-crud';

export const apiPrefix = '/api/GDToken/';


export function GetList(query: UserPageQuery, token: string) {
    return request({
        url: apiPrefix + token + '/get_activitylogs/',
        method: 'get',
        params: query,
    });
}


export function UpdateObj(data: EditReq, token: string) {
    return request({
        url: apiPrefix + token + '/edit_activity/',
        method: 'post',
        data: data,
    });
}


export function DelObj(id: string | number, token: string) {
    return request({
        url: apiPrefix + token + '/delete_activity/',
        method: 'post',
        data: {id},
    });
}
