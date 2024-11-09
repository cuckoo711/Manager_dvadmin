import {request} from '/@/utils/service';

export const apiPrefix = '/api/QuickUser/';

export async function GetPlayerDataByAny(
    game_id: number,
    checkView: string,
    checkTxt: string,
) {
    return request({
        url: apiPrefix + 'GetPlayerDataByAny/',
        method: 'post',
        data: {game_id: game_id, check_view: checkView, check_txt: checkTxt},
    });
}
