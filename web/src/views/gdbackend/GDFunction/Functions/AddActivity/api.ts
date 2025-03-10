import {request} from '/@/utils/service';

//upload_config
export async function UploadConfig(token_id: string, config: string) {
    return request({
        url: '/api/GDActiveConfig/upload_config/',
        method: 'post',
        data: {
            token_id: token_id,
            config: config
        }
    })
}

// check_config_exist
export async function CheckConfigExist(token_id: string) {
    return request({
        url: '/api/GDActiveConfig/check_config_exist/',
        method: 'get',
        params: {
            token_id: token_id
        }
    })
}
