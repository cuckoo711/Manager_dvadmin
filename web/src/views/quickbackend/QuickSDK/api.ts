import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

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

export async function SwitchGame(gameId: number) {
    return request({
        url: apiPrefix + 'SwitchGame/',
        method: 'post',
        data: { game_id: gameId },
    });
}
