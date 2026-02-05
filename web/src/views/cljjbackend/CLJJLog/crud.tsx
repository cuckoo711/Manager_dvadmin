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
                        show: auth("CLJJLog:Create")
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
                        show: auth("CLJJLog:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("CLJJLog:Delete")
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
                },
                search: {
                    title: '关键词',
                    column: {
                        show: false,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请输入关键词',
                        },
                    },
                    form: {
                        show: false,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                },
                id: {
                   title:"Id",
                   type:"text",
                   form: { show: false }
                },
                log: {
                   title:"日志",
                   type:"text",
                },
                ...commonCrudConfig()
            },
        },
    };
}
