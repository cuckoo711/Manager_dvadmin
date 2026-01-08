// // DSLHMergeTask API - Auto-generated on 2025-01-08 04:25:37

import {request} from '/@/utils/service';
import {InfoReq, UserPageQuery} from '@fast-crud/fast-crud';

export const apiPrefix = '/api/DSLHMergeTask/';

export function GetList(query: UserPageQuery) {
    return request({
        url: apiPrefix,
        method: 'get',
        params: query,
    });
}

export function GetObj(id: InfoReq) {
    return request({
        url: apiPrefix + id,
        method: 'get',
    });
}
