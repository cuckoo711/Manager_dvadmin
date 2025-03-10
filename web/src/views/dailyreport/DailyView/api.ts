import {request} from '/@/utils/service';

export const apiPrefix = "/api/"

export function getReport(data: any = null) {
    if (data == null) {
        return request({
            url: apiPrefix + 'reportdata/get_report/',
            method: 'get',
        });
    } else {
        return request({
            url: apiPrefix + 'reportdata/get_report/',
            method: 'post',
            data: data
        });
    }
}

