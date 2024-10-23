// // ServiceTableNormal API - Auto-generated on 2024-10-11 09:43:03

import {request} from '/@/utils/service';
import {UserPageQuery, AddReq, DelReq, EditReq, InfoReq} from '@fast-crud/fast-crud';


export const apiPrefix = '/api/ServiceTableNormal/';

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

export function DelObj(id: DelReq) {
    return request({
        url: apiPrefix + id + '/',
        method: 'delete',
        data: {id},
    });
}

export function generateServiceTable(id: any) {
    return request({
        url: apiPrefix + id + '/generateServiceTable/',
        method: 'get',
    });
}

export function DownloadFirst(id: any) {
    return request({
        url: apiPrefix + id + '/DownloadFirst/',
        method: 'get',
        responseType: 'blob',
    });
}


export function DownloadNoFirst(id: any) {
    return request({
        url: apiPrefix + id + '/DownloadNoFirst/',
        method: 'get',
        responseType: 'blob',
    });
}

export function batchGenerateServiceTable(data: any) {
    return request({
        url: apiPrefix + 'batchGenerateServiceTable/',
        method: 'post',
        data: data,
    });
}

export function batchDownloadServiceTable(data: any) {
    return request({
        url: apiPrefix + 'batchDownloadServiceTable/',
        method: 'post',
        data: data,
        responseType: 'blob',
    });
}

export function ClearServerTable() {
    return request({
        url: apiPrefix + 'cleanFiles/',
        method: 'get',
    });
}

export function batchSplitTaskServiceTable(data: any) {
    return request({
        url: apiPrefix + 'batchSplitTaskServiceTable/',
        method: 'post',
        data: data,
    });
}
