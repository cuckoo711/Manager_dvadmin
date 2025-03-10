import {request} from '/@/utils/service';


export async function GetGameServersList(query: any) {
    return request({
        url: '/api/GDServer/get_servers/',
        method: 'get',
        params: query
    });
}

export async function PushLog(log: string) {
    return request({
        url: '/api/GDLog/addlog/',
        method: 'post',
        data: {
            log: log
        }
    });
}

export async function GetGameServerInfo(game_id: string) {
    return request({
        url: '/api/GDServer/' + game_id + '/set_info/',
        method: 'get',
    })
}

export async function GetRoleInfo(token_id: string, sid: string, pid: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/get_pinfo/',
        method: 'post',
        params: {
            sid: sid,
            pid: pid
        }
    })
}

//del_gifts
export async function DelGifts(token_id: string, gift_ids: [string]) {
    return request({
        url: '/api/GDToken/' + token_id + '/del_gifts/',
        method: 'post',
        data: {
            gift_ids: gift_ids
        }
    })
}

//send_gifts
export async function SendGifts(token_id: string, server: string, gifts_name: string,
                                pname: string, gifts_id: string, des: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/send_gifts/',
        method: 'post',
        data: {
            server: server,
            gifts_name: gifts_name,
            pname: pname,
            gifts_id: gifts_id,
            des: des
        }
    })
}

//add_gifts
export async function AddGifts(token_id: string, gift_name: string, gift_des: string, gift_content: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/add_gifts/',
        method: 'post',
        data: {
            gift_name: gift_name,
            gift_des: gift_des,
            gift_content: gift_content
        }
    })
}

//edit_server_name
export async function EditServerName(token_id: string, serverid: string, newname: string, payload: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/edit_server_name/',
        method: 'post',
        data: {
            serverid: serverid,
            newname: newname,
            combinedServices: payload
        }
    })
}

//get_wifes_exist
export async function GetWifesList(token_id: string, server: string, pname: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/get_wifes_list/',
        method: 'get',
        params: {
            server: server,
            pname: pname
        }
    })
}

//del_wifes
export async function DelWifes(token_id: string, server: string, pname: string, wifes: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/del_wifes/',
        method: 'post',
        data: {
            server: server,
            pname: pname,
            wifeid: wifes
        }
    })
}

//add_wifes
export async function AddWifes(token_id: string, server: string, pname: string, wifes: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/add_wifes/',
        method: 'post',
        data: {
            server: server,
            pname: pname,
            wifeid: wifes
        }
    })
}

//edit_wifes
export async function EditWifes(token_id: string, server: string, pname: string, wifes: string, value: string, attrtype: 1 | 2 | 3) {
    return request({
        url: '/api/GDToken/' + token_id + '/edit_wifes/',
        method: 'post',
        data: {
            server: server,
            pname: pname,
            wifeid: wifes,
            value: value,
            attrtype: attrtype
        }
    })
}

//get_logs
export async function GetLogs(token_id: string, log_action: string, log_reason: string, log_server: string, log_pname: string, log_pid: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/get_logs/',
        method: 'get',
        params: {
            log_action: log_action,
            log_reason: log_reason,
            log_server: log_server,
            log_pname: log_pname,
            log_pid: log_pid
        }
    })
}
//get_latest_servers
export async function GetLatestServers(token_id: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/get_latest_servers/',
        method: 'get'
    })
}

//upload_server_activity
export async function UploadServerActivity(
    token_id: string,
    uploadServer: string,
    rangeStart: string,
    rangeEnd: string,
    startDate: string) {
    return request({
        url: '/api/GDToken/' + token_id + '/upload_server_activity/',
        method: 'post',
        data: {
            uploadServer: uploadServer,
            rangeStart: rangeStart,
            rangeEnd: rangeEnd,
            startDate: startDate
        }
    })
}
