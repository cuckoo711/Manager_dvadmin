import {request} from '/@/utils/service';

export const apiPrefix = '/api/QuickUser/';


export async function GetUser() {
    return request({
        url: apiPrefix + 'GetUser/',
        method: 'get',
    });
}

export async function GetGameList() {
    return request({
        url: apiPrefix + 'GetGameList/',
        method: 'get',
    });
}

export async function SwitchGame(gameId: number, channelSuffix: string) {
    return request({
        url: apiPrefix + 'SwitchGame/',
        method: 'post',
        data: {game_id: gameId, channel_suffix: channelSuffix},
    });
}

export async function GetChannelSuffix() {
    return request({
        url: apiPrefix + 'GetChannelSuffix/',
        method: 'get',
    });
}

export async function UpdateChannelStatus(
    gameId: number,
    batchSwitchType: number,
    multipleSelection: []
) {
    const data = {
        game_id: gameId,
        batch_switch_type: batchSwitchType,
        multiple_selection: multipleSelection
    }
    console.log(data)
    return request({
        url: apiPrefix + 'UpdateChannelStatus/',
        method: 'post',
        data: data,
    });
}
