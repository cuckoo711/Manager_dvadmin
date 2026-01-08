// GDLog CRUD TypeScript - Auto-generated on 2024-11-28 13:34:00

import * as api from './api';
import {
    AddReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';
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
            actionbar: {show: false},
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 100,
                buttons: {
                    view: {
                        type: 'text',
                        iconRight: 'View',
                    },
                    edit: {
                        show: false
                    },
                    remove: {
                        show: false
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
                }, creator_name: {}, log: {
                    title: "日志",
                    type: "text",
                    search: {show: true},
                    column: {
                        minWidth: '200',
                        showOverflowTooltip: true,
                    },
                    viewForm: {
                        component: {
                            props: {
                                type: 'textarea',
                                rows: 5
                            }
                        }
                    }
                },
                ...commonCrudConfig({
                    create_datetime: {table: true},
                    creator_name: {table: true, search: true},
                })
            },
        },
    };

}