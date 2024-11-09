// QuickUser CRUD TypeScript - Auto-generated on 2024-10-25 14:09:10

import * as api from './api';
import {
    dict,
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    compute,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import {request} from '/@/utils/service';
import {dictionary} from '/@/utils/dictionary';
import {successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
import {UpdateCookie} from "./api";
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
                buttons: {
                    add: {
                        show: auth("QuickUser:Create")
                    }
                }
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
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("QuickUser:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("QuickUser:Delete")
                    },
                    updateCookie: {
                        text: '更新cookie',
                        type: 'text',
                        iconRight: 'Refresh',
                        show: true,
                        click: async (obj) => {
                            await UpdateCookie(obj.row.id);
                            successMessage('更新成功');
                        }
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
                }, creator_name: {},username: {
                    title: "用户名",
                    type: "text",

                }, password: {
                    title: "密码",
                    type: "text",
                    column: {show: false},
                    form: {
                        component: {showPassword: true},
                    }

                }, expire_time: {
                    title: "过期时间",
                    type: "datetime",
                    form: {show: false},
                }, status: {
                    title: "状态",
                    type: "dict-select",
                    column: {
                        width: 100,
                        align: 'center',
                    },
                    form: {show: false},
                    dict: dict({
                        data: [{'label': '正常', 'value': '0', 'color': 'success'},
                            {'label': '失效', 'value': '1', 'color': 'danger'}],
                        label: "label",
                        value: "value"
                    })
                },
                ...commonCrudConfig({
                    creator_name: {table: true, },
                    update_datetime: {table: true},
                })
            },
        },
    };

}