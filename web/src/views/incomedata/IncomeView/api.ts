import {request} from '/@/utils/service';

export const apiPrefix = 'api/incomedata/';

export function getIncome(obj: any) {
    if (obj == null) {
        return request({
            url: apiPrefix + 'get_income/',
            method: 'get',
        });
    } else {
        return request({
            url: apiPrefix + 'get_income/',
            method: 'post',
            data: obj,
        });
    }
}

export function exportIncome(date: string, type: string) {
	return request({
		url: apiPrefix + 'export_data/',
		method: 'post',
        data: {
            date: date,
            type: type,
        },
	});
}

export function GetIncomeExport(obj: any) {
    return request({
        url: apiPrefix + 'get_income_export/',
        method: 'post',
        data: obj,
		responseType: 'blob',
    });
}
