// DSLHServer CRUD TypeScript - Auto-generated on 2024-12-26 10:04:44

import * as api from './api';
import {
    AddReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
import {ElMessage} from "element-plus";
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
                        show: auth("DSLHServer:Create")
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 220,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("DSLHServer:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("DSLHServer:Delete")
                    },
                    open_web: {
                        type: 'text',
                        text: '打开网页',
                        iconRight: 'Link',
                        show: true,
                        click: async (obj: any) => {
                            const url = obj.row.web_url + "login.php?gmname=" + obj.row.username + "&gmpswd=" + obj.row.password;
                            window.open(url)
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
                }, gamename: {
                    title: "游戏名",
                    type: "text",
                    form: {
                        rules: [{required: true, message: '请输入游戏名'}],
                    },
                    search: {show: true},
                }, server_host: {
                    title: "服务器地址",
                    type: "text",
                    form: {show: false},
                    search: {show: true},
                }, web_url: {
                    title: "网页地址",
                    type: "text",
                    form: {
                        rules: [{required: true, message: '请输入后台地址'}],
                    },
                    column: {show: false},
                    search: {show: true},
                }, username: {
                    title: "用户名",
                    type: "text",
                    form: {
                        rules: [{required: true, message: '请输入用户名'}],
                    },
                    search: {show: true},
                }, password: {
                    title: "密码",
                    type: "password",
                    form: {
                        rules: [{required: true, message: '请输入密码'}],
                    },
                    column: {show: false},
                }, ...commonCrudConfig({
                    update_datetime: {table: true}
                })
            },
        },
    };

}