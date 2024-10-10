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
            search: {
                show: false
            },
            toolbar: {
                show: false,
            },
            actionbar: {
                show: false,
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 150,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        show: auth("ServiceTableTemplate:Edit"),
                    },
                    remove: {
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
                }, creator_name: {}, channel: {
                    title: "所属渠道",
                    type: "dict-select",
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
                        url: '/api/channel_manage/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    })
                }, channel_name: {
                    title: "所属渠道",
                    type: "input",
                    column: {
                        align: 'center',
                        show: true,
                        width: 150,
                    },
                    form: {
                        show: false
                    },
                }, template_path: {
                    title: "模板路径",
                    type: "text",
                    form: {show: false},

                }, template_fields: {
                    title: "模板字段",
                    type: "textarea",
                    column: {show: false},

                }, is_split: {
                    title: "是否分表",
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('button_whether_number'),
                    }),

                }, is_enable: {
                    title: "是否启用",
                    type: 'dict-select',
                    form: {
                        rules: [{required: true, message: '请选择是否启用'}],
                    },
                    dict: dict({
                        data: dictionary('button_status_number'),
                    }),

                },
                ...commonCrudConfig({
                    creator_name: {table: true},
                    update_datetime: {table: true},
                    create_datetime: {table: true},
                })
            },
        },
    };

}