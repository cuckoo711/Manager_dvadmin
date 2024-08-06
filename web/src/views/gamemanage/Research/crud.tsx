// Research CRUD TypeScript - Auto-generated on 2024-05-20 13:55:43

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
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const response = await api.GetList(query);
        // 对获取的数据进行处理，将 alias 列表转换为中文顿号分隔的字符串
        response.data.forEach((item: any) => {
            if (item.alias && Array.isArray(item.alias)) {
                item.alias = item.alias.join('、');
            }
        });
        return response;
    };
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        // 将渠道别名从字符串转换为列表
        if (form.alias) {
            form.alias = form.alias.split('、').map((item: string) => item.trim());
        }
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        // 将渠道别名从字符串转换为列表
        if (form.alias) {
            form.alias = form.alias.split('、').map((item: string) => item.trim());
        }
        return await api.AddObj(form);
    };

    return {
        crudOptions: {
            pagination:{pageSize : 999},
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('research_manage:Create')
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
                        show: auth("research_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("research_manage:Delete")
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
                id: {
                    title: "Id",
                    type: "number",
                    form: {show: false},
                    column: {
                        show: false,
                    },
                }, name: {
                    title: "研发名称",
                    type: "text",
                    search: {
                        show: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入研发名称'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        width: 200,
                        align: 'center',
                    }
                }, alias: {
                    title: "研发别名",
                    type: "input",
                    form: {
                        rules: [
                            {required: true, message: '请输入研发别名'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                placeholder: '多个别名用顿号分隔，用中文顿号分隔'
                            },
                        }
                    },
                    column: {
                        width: 200,
                        showOverflowTooltip: true,
                    }
                }, company_name: {
                    title: "研发公司名",
                    type: "text",
                    search: {
                        show: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入研发公司名'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        width: 250,
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                }, research_ratio: {
                    title: "研发分成比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入研发分成比例'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    }

                }, slotting_ratio: {
                    title: "通道费比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入通道费比例'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    }

                }, research_tips: {
                    title: "研发备注",
                    type: "textarea",
                    column: {
                        align: 'center',
                        showOverflowTooltip: true,
                    },
                }, status: {
                    title: "研发状态",
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
                        data: dictionary('button_status_number'),
                    }),
                },
                ...commonCrudConfig()
            },
        },
    };

}