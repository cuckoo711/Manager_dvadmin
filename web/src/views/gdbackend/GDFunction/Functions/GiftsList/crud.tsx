import * as api from './api';
import {CreateCrudOptionsProps, CreateCrudOptionsRet, DelReq, dict, UserPageQuery} from '@fast-crud/fast-crud';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";

export const createCrudOptions = function (
    {crudExpose, GDGameBaseInfo}: CreateCrudOptionsProps & {
        GDGameBaseInfo: GDGameBaseInfoStates
    }): CreateCrudOptionsRet {

    let TempDatas = {
        "code": 2000,
        "data": [],
        "isNext": false,
        "is_previous": false,
        "limit": 50,
        "msg": "success",
        "page": 1,
        "total": 0
    }
    let TempQuery = {}

    const pageRequest = async (query: UserPageQuery) => {
        const {page, limit} = query;
        TempDatas = await api.GetList(TempQuery, GDGameBaseInfo.token)
        const start = (page - 1) * limit
        const end = start + limit
        const data = TempDatas.data.slice(start, end)

        TempDatas.page = page;
        TempDatas.limit = limit;
        TempDatas.total = TempDatas.data.length;

        console.log('pageRequest', data)
        return {
            code: 2000,
            data,
            isNext: TempDatas.isNext,
            isPrevious: TempDatas.is_previous,
            total: TempDatas.total,
            page,
            limit,
            msg: 'success'
        }
    };
    const delRequest = async ({row}: DelReq) => {
        const res = await api.DelObj(row.id, GDGameBaseInfo.token);
        if (res.code === 2000) {
            await crudExpose.doRefresh();
        }
        return res;
    };
    return {
        crudOptions: {
            request: {
                pageRequest,
                delRequest,
            },
            actionbar: {show: false},
            rowHandle: {
                width: 80,
                buttons: {
                    edit: {show: false},
                    view: {show: false},
                    remove: {
                        show: true,
                        text: '删除',
                        type: 'text',
                    },
                }
            },
            toolbar: {
                buttons: {
                    refresh: {show: false,},
                    compact: {show: false,},
                    export: {show: false,},
                    columns: {show: false,},
                },
            },
            search: {
                show: false,
                buttons: {
                    search: {text: '', circle: true,},
                    reset: {text: '', circle: true,},
                }
            },
            pagination: {
                pageSize: 20,
                "page-sizes": [50, 100, 200, 500, 1000],
            },
            table: {
                "row-key": "id",
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, // 禁止在列设置中选择
                    },
                },
                id: {
                    title: 'id',
                    form: {show: false},
                    column: {show: false},
                },
                name: {
                    title: '礼包名称',
                    type: 'text',
                    form: {show: false},
                    column: {width: 180},
                    search: {show: true},
                },
                giftDes: {
                    title: '礼包描述',
                    type: 'text',
                    form: {show: false},
                    search: {show: true},
                },
                gift: {
                    title: '礼包内容',
                    type: 'text',
                    form: {show: false},
                    search: {show: true},
                },
            }
        }
    }
}
