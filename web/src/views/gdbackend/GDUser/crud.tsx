// GDUser CRUD TypeScript - Auto-generated on 2024-08-26 09:36:42

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
                        show: auth("GDUser:Create")
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
                        show: auth("GDUser:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("GDUser:Delete")
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
                }, users: {
                    title: "关联用户",
                    type: "text",

                }, username: {
                    title: "用户名",
                    type: "text",

                }, password: {
                    title: "密码",
                    type: "password",
                    column: {show: false},
                    form: {
                        rules: [
                            {required: true, message: '请输入密码', trigger: 'blur'},
                        ],
                    }

                }, token: {
                    title: "Token",
                    type: "password",
                    column: {show: false},
                    form: {show: false},
                },
            },
        },
    };

}