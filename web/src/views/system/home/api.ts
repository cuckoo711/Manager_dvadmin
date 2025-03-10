import {request} from '/@/utils/service';

export const apiPrefix = "/api/"


export function getData() {
    return request({
        url: apiPrefix + 'daylidata/get_datas/',
        method: 'get',
    })
}
