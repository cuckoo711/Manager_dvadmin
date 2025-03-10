// DSLHMergeTask CRUD TypeScript - Auto-generated on 2025-01-08 04:25:37

import * as api from './api';
import {CreateCrudOptionsProps, CreateCrudOptionsRet, dict, UserPageQuery} from '@fast-crud/fast-crud';
import {commonCrudConfig} from "/@/utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
    };

    return {
        crudOptions: {
            request: {pageRequest,},
            actionbar: {show: false,},
            rowHandle: {
                fixed: 'right',
                width: 80,
                align: 'center',
                buttons: {
                    view: {
                        show: true,
                        type: 'text',
                        text: '查看',
                        iconRight: 'view',
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        show: false,
                    },
                },
            },
            search: {show: false},
            form: {
                col: {span: 24},
                labelWidth: '110px',
                wrapper: {
                    is: 'el-dialog',
                    width: '600px',
                },
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                    },

                }, output_dir: {
                    title: "输出目录",
                    type: "text",
                    column: {
                        align: 'center',
                        width: '350',
                    }
                }, start_id: {
                    title: "起始Id",
                    type: "number",
                    column: {
                        align: 'center',
                        width: '100'
                    }

                }, end_id: {
                    title: "结束Id",
                    type: "number",
                    column: {
                        align: 'center',
                        width: '100'
                    }

                }, dest_id: {
                    title: "目标Id",
                    type: "text",
                    column: {
                        align: 'center',
                        width: '100'
                    }

                }, merge_ids: {
                    title: "合服服务器Id列表",
                    type: "text",

                }, merged_ids: {
                    title: "已合服服务器Id列表",
                    type: "text",

                }, remote_ip: {
                    title: "服务器Ip",
                    type: "text",
                    column:{
                        width: '150',
                    }

                }, prefix: {
                    title: "数据库前缀",
                    type: "text",

                }, task_status: {
                    title: "任务状态",
                    type: "dict-select",
                    dict: dict({
                        data: [
                            {'label': '未开始', 'value': 0, 'color': 'info'},
                            {'label': '进行中', 'value': 1, 'color': 'primary'},
                            {'label': '已完成', 'value': 2, 'color': 'success'},
                            {'label': '失败', 'value': 3, 'color': 'danger'}
                        ],
                        label: "label",
                        value: "value"
                    }),
                    column:{
                        width: '100',
                    }
                },
                logs: {
                    title: "日志",
                    type: "textarea",
                    column: {
                        show: false
                    },
                    viewForm: {
                        component: {
                            placeholder: '暂无日志',
                            showWordLimit: true,
                            rows: 5,
                        }
                    }
                },
                ...commonCrudConfig()
            },
        },
    };

}