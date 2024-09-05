// 将文件传到后端
import { request } from '/@/utils/service';

export const apiPrefix = 'api/manage/upload/';

export function UploadDDDD(obj: any) {
    return request({
        url: 'api/manage/upload/' + 'dddd/',
        method: 'post',
        data: obj,
    });
}
