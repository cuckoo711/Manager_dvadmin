// ServiceTableNormal CRUD TypeScript - Auto-generated on 2024-10-11 09:43:03

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
                        show: auth("ServiceTableNormal:Create")
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
                        show: auth("ServiceTableNormal:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("ServiceTableNormal:Delete")
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
                   type:"unknown",
                   
                },description: {
                   title:"描述",
                   type:"text",
                   
                },creator: {
                   title:"创建人",
                   type:"unknown",
                   
                },modifier: {
                   title:"修改人",
                   type:"text",
                   
                },dept_belong_id: {
                   title:"数据归属部门",
                   type:"text",
                   
                },update_datetime: {
                   title:"修改时间",
                   type:"datetime",
                   
                },create_datetime: {
                   title:"创建时间",
                   type:"datetime",
                   
                },game_name: {
                   title:"游戏名称",
                   type:"text",
                   
                },open_name: {
                   title:"初始区服名称",
                   type:"text",
                   
                },open_datetime: {
                   title:"开服时间",
                   type:"datetime",
                   
                },open_frequency: {
                   title:"开服频率",
                   type:"number",
                   
                },open_count: {
                   title:"开服数量",
                   type:"number",
                   
                },copy_content: {
                   title:"复制内容",
                   type:"text",
                   
                },first_service_path: {
                   title:"首服文件路径",
                   type:"text",
                   
                },no_first_service_path: {
                   title:"无首服文件路径",
                   type:"text",
                   
                },generate_status: {
                   title:"生成状态",
                   type:"select",
                   dict:dict({
                     data:[{'label': '未生成', 'value': '0'}, {'label': '已生成', 'value': '1'}],
                     label:"label",
                     value:"value"
                   })
                },
            },
        },
    };

}