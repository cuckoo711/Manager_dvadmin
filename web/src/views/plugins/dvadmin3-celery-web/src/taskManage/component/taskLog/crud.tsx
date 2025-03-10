import * as api from './api';
import {
    AddReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq,
    dict,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';

export const createCrudOptions = function ({crudExpose, context}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const datas = await api.GetList({...query, ...{name: context!.taskItem.name}});
        datas.data.forEach((item: any) => {
            if (!item.periodic_task_name) {
                item.periodic_task_name = item.task_name;
            }
            if (item.result) {
                try {
                    const outerResult = JSON.parse(item.result);

                    if (outerResult.data && typeof outerResult.data === 'string') {
                        outerResult.data = JSON.parse(outerResult.data);
                    }

                    item.result = JSON.stringify(outerResult, null, 2);
                } catch (error) {
                    console.error('解析 JSON 出错:', error);
                    item.result = '';
                }
            } else {
                item.result = '';
            }
        });
        return datas;
    };
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        return await api.AddObj(form);
    };

    return {
        crudOptions: {
            actionbar: {
                show: false,
            },
            toolbar: {
                show: false,
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            rowHandle: {
                show: false,
            },
            form: {
                col: {span: 24},
                labelWidth: '110px',
                wrapper: {
                    is: 'el-dialog',
                    width: '600px',
                },
            },
            search: {
                defaultSpan: 6,
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        //type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                        //@ts-ignore
                        formatter: (context) => {
                            //计算序号,你可以自定义计算规则，此处为翻页累加
                            let index = context.index ?? 1;
                            let pagination: any = crudExpose!.crudBinding.value.pagination;
                            return ((pagination.currentPage ?? 1) - 1) * pagination.pageSize + index + 1;
                        },
                    },
                },
                task_id: {
                    title: '任务ID',
                    search: {show: true},
                    type: 'text',
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                periodic_task_name: {
                    title: '任务名称',
                    search: {show: true},
                    type: 'text',
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                status: {
                    title: '执行状态',
                    search: {show: true},
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            {
                                label: '执行成功',
                                value: 'SUCCESS',
                                color: 'success',
                                effect: 'dark',
                            },
                            {
                                label: '已开始',
                                value: 'STARTED',
                                effect: 'dark',
                            },
                            {
                                label: '已取消',
                                value: 'REVOKED',
                                effect: 'dark',
                            },
                            {
                                label: '重试中',
                                value: 'RETRY',
                                effect: 'dark',
                            },
                            {
                                label: '已收到',
                                value: 'RECEIVED',
                                effect: 'dark',
                            },
                            {
                                label: '待定中',
                                value: 'PENDING',
                                effect: 'dark',
                            },
                            {
                                label: '执行失败',
                                value: 'FAILURE',
                                effect: 'dark',
                                color: 'error',
                            },
                        ],
                    }),
                },
                result: {
                    title: '执行结果',
                    column: {
                        showOverflowTooltip: true,
                    },
                },
                date_created: {
                    title: '创建时间',
                    type: 'datetime',
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                date_done: {
                    title: '完成时间',
                    type: 'datetime',
                    column: {
                        showOverflowTooltip: true,
                    }
                },
                worker: {
                    title: '执行节点',
                    type: 'text',
                    column: {
                        showOverflowTooltip: true,
                    }
                },
            },
        },
    };
};
