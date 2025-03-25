// GDServer CRUD TypeScript - Auto-generated on 2024-08-26 09:36:48

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
import {APIResponseData} from "/@/views/system/dept/types";
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
                        show: auth("GDServer:Create")
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
                        show: auth("GDServer:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("GDServer:Delete")
                    },
                    open_web: {
                        type: 'text',
                        text: '打开网页',
                        iconRight: 'Link',
                        show: true,
                        click: async (obj: any) => {
                            window.open(obj.row.web_url)
                        }
                    }
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

                }, server_port: {
                    title: "服务器端口",
                    type: "text",
                    form: {show: false},

                }, web_url: {
                    title: "网页地址",
                    type: "text",
                    form: {
                        rules: [{required: true, message: '请输入后台地址'}],
                    },
                    column: {show: false},
                    search: {show: true},
                }, sql_pwd: {
                    title: "数据库密码",
                    type: "text",
                    view: {show: false},
                    form: {
                        show: false,
                    },
                    editForm: {
                        show: true,
                    },
                    column: {show: false},
                }, is_active: {
                    title: "是否启用",
                    search: {
                        show: true,
                    },
                    type: 'dict-radio',
                    column: {
                        width: 120,
                        component: {
                            name: 'fs-dict-switch',
                            activeText: '',
                            inactiveText: '',
                            style: '--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6',
                            onChange: compute((context) => {
                                return () => {
                                    api.UpdateObj(context.row).then((res: APIResponseData) => {
                                        successMessage(res.msg as string);
                                    });
                                };
                            }),
                        },
                    },
                    dict: dict({
                        data: dictionary('button_status_bool'),
                    }),
                },
                ...commonCrudConfig({
                    update_datetime: {table: true},
                })
            },
        },
    };

}