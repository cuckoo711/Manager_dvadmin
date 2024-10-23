// // Consoles API - Auto-generated on 2024-07-12 13:49:43

import {downloadFile, request} from '/@/utils/service';
import {UserPageQuery, AddReq, DelReq, EditReq, InfoReq} from '@fast-crud/fast-crud';

export const apiPrefix = '/api/consoles/';

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

export function AddObj(obj: AddReq) {
    return request({
        url: apiPrefix,
        method: 'post',
        data: obj,
    });
}

export function UpdateObj(obj: EditReq) {
    return request({
        url: apiPrefix + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

export function RenewObj(obj: EditReq) {
    return request({
        url: apiPrefix + obj.id + '/renew/',
        method: 'put',
        data: obj,
    });
}

export function DelObj(id: DelReq) {
    return request({
        url: apiPrefix + id + '/',
        method: 'delete',
        data: {id},
    });
}

export function ManualRefresh() {
    return request({
        url: apiPrefix + 'manual_refresh/',
        method: 'get',
    });
}

export function exportData(params: any) {
	return downloadFile({
		url: apiPrefix + 'export_data/',
		params: params,
		method: 'get',
	});
}
