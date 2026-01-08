import * as api from './api';
import {CreateCrudOptionsProps, CreateCrudOptionsRet, DelReq, dict, EditReq, UserPageQuery} from '@fast-crud/fast-crud';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";
import {ElMessage, ElMessageBox} from "element-plus";

export const createCrudOptions = function (
    {crudExpose, GDGameBaseInfo, handleLogger, handleReload}: CreateCrudOptionsProps & {
        GDGameBaseInfo: GDGameBaseInfoStates, handleLogger: Function, handleReload: Function
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
    let TempQuery: any = {}

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
    const editRequest = async ({form}: EditReq) => {
        await api.UpdateObj(form, GDGameBaseInfo.token).then((res: any) => {
            if (res.data) {
                handleLogger(`修改游戏${GDGameBaseInfo.data.GameName}活动成功: ${form}`)
                ElMessage.success('修改成功')
            } else {
                ElMessage.error('修改失败, 请检查修改参数')
            }
        }).catch((err: any) => {
            ElMessage.error('修改失败, 请检查修改参数')
        })
        return true
    };

    const delRequest = async ({row}: DelReq) => {
        await api.DelObj(row.id, GDGameBaseInfo.token).then((res: any) => {
            if (res.data) {
                handleLogger(`删除游戏${GDGameBaseInfo.data.GameName}活动成功: ${row}`)
                ElMessage.success('删除成功')
            } else {
                ElMessage.error('删除失败, 请检查删除参数')
            }
        }).catch((err: any) => {
            ElMessage.error('删除失败, 请检查删除参数')
        })
    };


    return {
        crudOptions: {
            request: {
                pageRequest,
                editRequest,
                delRequest,
                handleLogger,
            },
            actionbar: {
                buttons: {
                    add: {show: false,},
                    batchDel: {
                        show: true,
                        text: '全部删除',
                        icon: 'Delete',
                        title: '全部删除',
                        type: 'primary',
                        click: async () => {
                            const datas = TempDatas.data
                            if (!datas.length) {
                                ElMessage.error('没有数据可删除')
                                return
                            }
                            const serverids = TempQuery.serverid?.toString()
                            if (!serverids) {
                                ElMessage.error('请务必先选择区服')
                                return
                            }
                            const actids = datas.map((item: any) => item.id)
                            //用:合并活动id
                            const actid = actids.join(':')
                            await ElMessageBox.confirm(
                                `此操作将直接删除该区服所有活动, 共 ${actids.length} 个活动, 请谨慎操作, 是否继续?`,
                                '提示', {
                                    confirmButtonText: '确定',
                                    cancelButtonText: '取消',
                                    type: 'warning'
                                }).then(async () => {
                                await api.DelObj(actid, GDGameBaseInfo.token).then((res: any) => {
                                    if (res.data) {
                                        handleLogger(`删除游戏${GDGameBaseInfo.data.GameName}的区服[${serverids}]活动成功, 共 ${actids.length} 个活动`)
                                        ElMessage.success('删除成功')
                                    } else {
                                        ElMessage.error('删除失败, 请检查删除参数')
                                    }
                                }).catch(() => {
                                    ElMessage.error('删除失败, 请检查删除参数')
                                })
                            }).catch(() => {
                                    ElMessage.info('已取消删除')
                                }
                            )
                        }
                    },
                }
            },
            toolbar: {
                show: false,
            },
            rowHandle: {
                width: 180,
                buttons: {
                    view: {show: false},
                    edit: {
                        iconRight: 'EditPen',
                        type: 'text',
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                    },
                }
            },
            search: {
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
            form: {},
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
                server: {
                    title: '服务器',
                    type: 'text',
                    form: {show: false},
                    column: {
                        width: 150,
                        showOverflowTooltip: true,
                    },
                },
                serverid: {
                    title: '所属区服',
                    type: 'dict-select',
                    column: {show: false},
                    form: {show: false},
                    search: {show: true},
                    dict: dict({
                        data: GDGameBaseInfo.data.Servers,
                        value: 'value',
                        label: 'label',
                    })
                },
                type: {
                    title: '活动类型',
                    type: 'dict-select',
                    column: {
                        show: true,
                        component: {
                            color: 'primary'
                        }
                    },
                    form: {show: false},
                    search: {
                        show: true,
                        component: {
                            filterable: true
                        }
                    },
                    dict: dict({
                        data: GDGameBaseInfo.data.Activetype,
                        value: 'value',
                        label: 'label',
                        color: 'seccess'
                    })
                },
                name: {
                    title: '活动名称',
                    type: 'text',
                    form: {
                        show: true,
                        rules: [
                            {required: true, message: '请输入活动名称'}
                        ]
                    },
                    search: {show: false},
                },
                des: {
                    title: '活动描述',
                    type: 'textarea',
                    form: {
                        show: true,
                        col: {span: 24},
                        rules: [
                            {required: true, message: '请输入活动描述'}
                        ]
                    },
                    search: {show: false},
                    column: {
                        showOverflowTooltip: true,
                    },
                },
                param: {
                    title: '活动参数',
                    type: 'textarea',
                    form: {
                        show: true,
                        col: {span: 24},
                        rules: [
                            {required: true, message: '请输入活动参数'}
                        ]
                    },
                    search: {show: false},
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                startTime: {
                    title: "开始时间",
                    type: "datetime",
                    form: {
                        show: true,
                        rules: [
                            {required: true, message: '请输入开始时间'}
                        ]
                    },
                    column: {
                        width: 180,
                        sortable: true,
                        format: 'YYYY-MM-DD',
                    },
                    search: {
                        show: true,
                        component: {
                            type: 'date',
                            props: {
                                'placeholder': '开始时间',
                                'value-format': 'YYYY-MM-DD',
                            }
                        },
                        valueResolve(context: any) {
                            const {value} = context
                            //value解析，就是把组件的值转化为后台所需要的值
                            //在form表单点击保存按钮后，提交到后台之前执行转化
                            if (value) {
                                context.form.qstime = value + ' 00:00:00'
                            }
                        }
                    },
                },
                endTime: {
                    title: "结束时间",
                    type: "datetime",
                    column: {
                        width: 180,
                        sortable: true,
                        format: 'YYYY-MM-DD',
                    },
                    form: {
                        show: true,
                        rules: [
                            {required: true, message: '请输入开始时间'}
                        ]
                    },
                    search: {
                        show: true,
                        component: {
                            type: 'date',
                            props: {
                                'placeholder': '结束时间',
                                'value-format': 'YYYY-MM-DD',
                            }
                        },
                        valueResolve(context: any) {
                            const {value} = context
                            //value解析，就是把组件的值转化为后台所需要的值
                            //在form表单点击保存按钮后，提交到后台之前执行转化
                            if (value) {
                                context.form.qetime = value + ' 23:59:59'
                            }
                        }
                    },
                },
                disTime: {
                    title: "隐藏时间",
                    type: "datetime",
                    column: {
                        width: 180,
                        sortable: true,
                        format: 'YYYY-MM-DD HH:mm:ss',
                    },
                    form: {
                        show: true,
                        rules: [
                            {required: true, message: '请输入开始时间'}
                        ]
                    },
                },

            },
        },
    };
};
