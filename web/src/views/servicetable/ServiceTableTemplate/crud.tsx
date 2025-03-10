// ServiceTableTemplate CRUD TypeScript - Auto-generated on 2024-10-10 10:49:30

import * as api from './api';
import {
    AddReq,
    compute,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq,
    dict,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';
import {dictionary} from '/@/utils/dictionary';
import {successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const lists = await api.GetList(query);
        lists.data.forEach((item: any) => {
            if (item.template_path) {
                // 创建新的对象格式
                item.template_path = item.template_path.split('/').pop()
            }
        });
        return lists;
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
                buttons: {
                    add: {
                        show: auth("ServiceTableTemplate:Create")
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 120,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        type: 'text',
                        show: auth("ServiceTableTemplate:Update")
                    },
                    remove: {
                        type: 'text',
                        show: auth("ServiceTableTemplate:Delete")
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
                }, channel: {
                    title: "渠道名称",
                    type: "dict-select",
                    search: {show: true},
                    column: {
                        show: false,
                    },
                    form: {
                        rules: [{required: true, message: '请选择渠道名称'}],
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                    dict: dict({
                        url: '/api/ServiceTableChannel/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    })
                }, template_name: {
                    title: "模板名称",
                    type: "input",
                    form: {
                        rules: [{required: true, message: '请输入模板名称'}],
                    },
                    column: {
                        align: 'center',
                        show: true,
                        width: 200,
                    },
                },
                channel_name: {
                    title: "所属渠道",
                    type: "input",
                    column: {
                        align: 'center',
                        show: true,
                        width: 200,
                    },
                    form: {
                        show: false
                    },
                }, template_fields: {
                    title: "模板字段",
                    type: "textarea",
                    form: {
                        rules: [{required: true, message: '请输入模板字段'}],
                    },
                    column: {
                        align: 'center',
                        show: true,
                        showOverflowTooltip: true,
                    },

                }, is_split: {
                    title: "是否分表",
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            {'label': '是', 'value': '1', 'color': 'success'},
                            {'label': '否', 'value': '2', 'color': 'warning'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        width: 100
                    },
                    search: {show: true},

                }, output_format: {
                    title: "输出格式",
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            {'label': 'xls', 'value': '0', 'color': 'primary'},
                            {'label': 'xlsx', 'value': '1', 'color': 'success'},
                            {'label': 'csv', 'value': '2', 'color': 'info'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        width: 100
                    },
                    search: {show: true},
                }, output_engine: {
                    title: "输出引擎",
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            {'label': 'ExcelWriter', 'value': '0', 'color': 'primary'},
                            {'label': 'DataFrame', 'value': '1', 'color': 'success'},
                            {'label': 'Workbook', 'value': '2', 'color': 'info'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        width: 100
                    },
                    search: {show: true},
                }, is_enable: {
                    title: "是否启用",
                    type: 'dict-select',
                    form: {
                        rules: [{required: true, message: '请选择是否启用'}],
                    },
                    dict: dict({
                        data: [
                            {'label': '启用', 'value': '1', 'color': 'success'},
                            {'label': '禁用', 'value': '0', 'color': 'warning'},
                        ],
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        width: 100,
                        show: true,
                    },
                    search: {show: true},

                },
                ...commonCrudConfig({
                    update_datetime: {table: true},
                })
            },
        },
    };

}