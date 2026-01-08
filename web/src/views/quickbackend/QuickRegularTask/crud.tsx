// QuickRegularTask CRUD TypeScript - Auto-generated on 2025-02-20 20:43:12

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
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
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
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            actionbar: {
                // buttons: {
                //     add: {
                //         show: auth("QuickRegularTask:Create")
                //     }
                // }
                show: false
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 150,
                buttons: {
                    view: {
                        type: 'text',
                        iconRight: 'View',
                        show: true
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("QuickRegularTask:Delete")
                    },
                },
            },
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
                }, game_id: {
                    title: "游戏ID",
                    type: "text",
                    search: {show: true},

                }, game_name: {
                    title: "游戏名",
                    type: "text",
                    column: {
                        minWidth: '150',
                        showOverflowTooltip: true,
                    },
                    search: {show: true},

                }, task_desc: {
                    title: "任务描述",
                    type: "textarea",
                    column: {
                        minWidth: '200',
                        showOverflowTooltip: true,
                    },
                    search: {show: true},

                }, task_date: {
                    title: "执行日期",
                    type: "date",
                    column: {
                        width: '150',
                    },
                    form: {
                        component: {
                            props: {
                                type: 'date',
                                format: 'YYYY-MM-DD',
                                'value-format': 'YYYY-MM-DD',
                            }
                        }
                    },
                    search: {
                        show: true,
                        col: {span: 8},
                        component: {
                            type: "daterange",
                            props: {
                                "start-placeholder": "开始时间",
                                "end-placeholder": "结束时间",
                                "value-format": "YYYY-MM-DD",
                                "picker-options": {
                                    shortcuts: [
                                        {
                                            text: "最近一周",
                                            onClick(picker: any) {
                                                const end = new Date();
                                                const start = new Date();
                                                start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                                                picker.$emit("pick", [start, end]);
                                            },
                                        },
                                        {
                                            text: "最近一个月",
                                            onClick(picker: any) {
                                                const end = new Date();
                                                const start = new Date();
                                                start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                                                picker.$emit("pick", [start, end]);
                                            },
                                        },
                                        {
                                            text: "最近三个月",
                                            onClick(picker: any) {
                                                const end = new Date();
                                                const start = new Date();
                                                start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                                                picker.$emit("pick", [start, end]);
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                        valueResolve(context: any) {
                            const {value} = context;
                            if (value) {
                                // 假设 value 是一个数组并且 value[0] 和 value[1] 都是日期字符串
                                const startDate = value[0];
                                const endDate = value[1];

                                // 仅示例：如果只想要“日期”部分，则可做如下处理
                                if (typeof startDate === "string") {
                                    context.form.task_date_after = startDate.split(" ")[0];
                                }
                                if (typeof endDate === "string") {
                                    context.form.task_date_before = endDate.split(" ")[0];
                                }
                            }
                        },
                    },
                }, remaining_days: {
                    title: "剩余天数",
                    type: "text",
                    column: {
                        width: '100',
                    },
                    search: {
                        show: true,
                        component: {
                            type: "input-number",
                            props: {
                                controls: false,
                                min: 0,
                                "value-format": "Number",
                            },
                        },
                    }
                }, task_type: {
                    title: "任务类型",
                    type: "dict-select",
                    dict: dict({
                        data: [
                            {'label': '批量关注册', 'value': '0', 'color': 'warning'},
                            {'label': '批量关支付', 'value': '1', 'color': 'warning'},
                            {'label': '批量关登录', 'value': '2', 'color': 'warning'},
                            {'label': '批量开注册', 'value': '3', 'color': 'success'},
                            {'label': '批量开支付', 'value': '4', 'color': 'success'},
                            {'label': '批量开登录', 'value': '5', 'color': 'success'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    search: {show: true},
                }, status: {
                    title: "状态",
                    type: "dict-select",
                    dict: dict({
                        data: [
                            {'label': '未执行', 'value': '0', 'color': 'info'},
                            {'label': '已执行', 'value': '1', 'color': 'success'},
                            {'label': '执行失败', 'value': '2', 'color': 'danger'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    search: {show: true},
                },
                ...commonCrudConfig({
                    create_datetime: {table: true},
                    creator_name: {table: true, search: true},
                })
            },
        },
    };

}