import {request} from '/@/utils/service';

export async function GetGameServersList(query: any) {
    return request({
        url: '/api/DSLHServer/get_servers/',
        method: 'get',
        params: query
    });
}

export async function PushLog(log: string) {
    return request({
        url: '/api/DSLHLog/addlog/',
        method: 'post',
        data: {
            log: log
        }
    });
}

export async function GetGameServerAdminInfo(game_id: string) {
    return request({
        url: '/api/DSLHServer/' + game_id + '/get_admin_info/',
        method: 'get',
    })
}

//megeropt
export async function GetGameServerMergeOpt(game_id: string, datas: any) {
    return request({
        url: '/api/DSLHServer/' + game_id + '/megeropt/',
        method: 'post',
        data: datas,
    })
}

//megersql
export async function GetGameServerMergeSql(datas: any) {
    return request({
        url: '/api/DSLHServer/megersql/',
        method: 'post',
        data: datas,
    })
}