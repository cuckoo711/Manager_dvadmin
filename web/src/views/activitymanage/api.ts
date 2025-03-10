import {request} from '/@/utils/service';

// get_all_activities_game_names
export async function GetAllActivitiesGameNames() {
    return request({
        url: '/api/activity_game/get_all_activities_game_names/',
        method: 'get',
    })
}

// get_activities_by_game_name
export async function GetActivitiesByGameName(
    game_name: string,
    activity_name: string,
    keyword: string,
) {
    return request({
        url: '/api/activity_content/get_activities_by_game_name/',
        method: 'post',
        data: {
            game_name: game_name,
            activity_name: activity_name,
            keyword: keyword
        }
    })
}

// get_activity_content
export async function GetActivityContent(activity_id: string) {
    return request({
        url: '/api/activity_content/get_activity_content/',
        method: 'post',
        data: {
            activity_id: activity_id
        }
    })
}