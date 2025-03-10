import * as api from './api';
import {CreateCrudOptionsProps, CreateCrudOptionsRet, dict, UserPageQuery} from '@fast-crud/fast-crud';
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
        const {page, limit, ...nonPaginationQuery} = query;
        if (JSON.stringify(nonPaginationQuery) !== JSON.stringify(TempQuery)) {
            TempDatas.data = []
            TempQuery = {...nonPaginationQuery}
        }

        if (!TempDatas.data.length) {
            TempDatas = await api.GetList(TempQuery, GDGameBaseInfo.token)
        }

        const start = (page - 1) * limit
        const end = start + limit
        const data = TempDatas.data.slice(start, end)

        TempDatas.page = page;
        TempDatas.limit = limit;
        TempDatas.total = TempDatas.data.length;

        console.log('pageRequest', data   )
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


    return {
        crudOptions: {
            request: {
                pageRequest,
            },
            actionbar: {show: false},
            toolbar: {
                buttons: {
                    refresh: {show: false,},
                    compact: {show: false,},
                    export: {show: false,},
                    columns: {show: false,},
                },
            },
            rowHandle: {show: false},
            search: {
                show: false,
                buttons: {
                    search: {text: '', circle: true,},
                    reset: {text: '', circle: true,},
                }
            },
            pagination: {
                pageSize: 50,
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
                    search: {show: false},
                    column: {show: false},
                },
                time: {
                    title: '发件时间',
                    type: 'datetime',
                    form: {show: false},
                    column: {
                        width: 180,
                        sortable: true,
                        format: 'YYYY-MM-DD HH:mm:ss',
                    },
                    search: {
                        show: true,
                        col: {span: 8},
                        component: {
                            type: 'datetimerange',
                            props: {
                                'start-placeholder': '开始时间',
                                'end-placeholder': '结束时间',
                                'value-format': 'YYYY-MM-DD HH:mm:ss',
                            }
                        },
                        valueResolve(context: any) {
                            const {value} = context
                            //value解析，就是把组件的值转化为后台所需要的值
                            //在form表单点击保存按钮后，提交到后台之前执行转化
                            if (value) {
                                context.form.startTime = value[0]
                                context.form.stopTime = value[1]
                            }
                        }
                    },
                },
                serverName: {
                    title: '所属区服',
                    type: 'dict-select',
                    column: {show: false},
                    form: {show: false},
                    search: {show: true},
                    dict: dict({
                        data: GDGameBaseInfo.data.Servers,
                        value: 'label',
                        label: 'label',
                    })
                },
                serverId: {
                    title: '所属区服',
                    search: {show: false},
                    form: {show: false},
                    column: {
                        minwidth: 180,
                        sortable: true,
                        align: 'center',
                    }
                },
                gmName: {
                    title: '发件GM',
                    search: {show: false},
                    form: {show: false},
                    column: {
                        minwidth: 180,
                        sortable: true,
                        align: 'center',
                    }
                },
                playerNames: {
                    title: '收件玩家',
                    type: 'text',
                    search: {show: true},
                    form: {show: false},
                },
                name: {
                    title: '邮件标题',
                    search: {show: false},
                    form: {show: false},
                },
                reason: {
                    title: '邮件内容',
                    search: {show: false},
                    form: {show: false},
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                prop: {
                    title: '道具',
                    type: 'dict-select',
                    search: {
                        show: true,
                        filterable: true,
                    },
                    form: {show: false},
                    column: {show: false,},
                    dict: dict({
                        data: GDGameBaseInfo.data.SidsDict.props,
                        value: 'value',
                        label: 'label',
                    })
                },
                gift: {
                    title: '道具代码',
                    search: {show: false},
                    form: {show: false},
                    column: {
                        showOverflowTooltip: true,
                    }
                },
            },
        },
    };
};
