import {request} from '/@/utils/service';
import { UserPageQuery} from '@fast-crud/fast-crud';


export function GetList(query: UserPageQuery, token: string) {
    return request({
        url: '/api/GDToken/' + token + '/get_giftslogs/',
        method: 'get',
        params: query,
    });
}

