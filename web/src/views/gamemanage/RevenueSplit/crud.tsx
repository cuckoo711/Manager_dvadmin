import * as api from './api';
import {
    dict,
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import {auth} from '/@/utils/authFunction';
import {commonCrudConfig} from "/@/utils/commonCrud";
import {ElMessage} from "element-plus";
import {exportData} from "./api";

export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => await api.GetList(query);
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => await api.DelObj(row.id);
    const addRequest = async ({form}: AddReq) => await api.AddObj(form);
    const exportRequest = async (query: UserPageQuery) => {
        return api.exportData(query);
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
                        show: auth('revenue_split_manage:Create')
                    },
                    export: { //这个export便是导出的按钮
                        text: "导出",//按钮文字
                        title: "导出",//鼠标停留显示的信息
                        click() {
                            return exportRequest(crudExpose!.getSearchFormData())
                        },

                    }
                }
            },
            rowHandle: {
                fixed: 'right',
                width: 150,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("revenue_split_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("revenue_split_manage:Delete")
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
                        columnSetDisabled: true,
                    },
                }, id: {
                    title: 'ID',
                    type: 'text',
                    form: {show: false},
                    column: {show: false},
                }, game: {
                    title: "游戏名称",
                    type: "dict-select",
                    column: {
                        show: false,
                    },
                    form: {
                        rules: [{required: true, message: '请选择游戏名称'}],
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                    dict: dict({
                        url: '/api/game_manage/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    })
                }, game_name: {
                    title: "游戏名称",
                    type: "text",
                    column: {
                        align: 'center',
                        show: true,
                        width: 350,
                        showOverflowTooltip: true,
                    },
                    search: {
                        show: true,
                    },
                    form: {show: false}
                }, channel: {
                    title: "渠道名称",
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
                    title: "渠道名称",
                    type: "text",
                    column: {
                        align: 'center',
                        show: true,
                        width: 150,
                    },
                    search: {
                        show: true,
                    },
                    form: {show: false}
                }, game_release_date: {
                    title: "游戏发行日期",
                    type: "date",
                    search: {
                        show: true,
                        col: {span: 8},
                        component: {
                            type: 'datetimerange',
                            props: {
                                'start-placeholder': '起始日期',
                                'end-placeholder': '结束日期',
                                'value-format': 'YYYY-MM-DD',
                                'picker-options': {
                                    shortcuts: [{
                                        text: '最近一周',
                                        onClick(picker) {
                                            const end = new Date();
                                            const start = new Date();
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                                            picker.$emit('pick', [start, end]);
                                        }
                                    }, {
                                        text: '最近一个月',
                                        onClick(picker) {
                                            const end = new Date();
                                            const start = new Date();
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                                            picker.$emit('pick', [start, end]);
                                        }
                                    }, {
                                        text: '最近三个月',
                                        onClick(picker) {
                                            const end = new Date();
                                            const start = new Date();
                                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                                            picker.$emit('pick', [start, end]);
                                        }
                                    }]
                                }
                            }
                        },
                        valueResolve(context: any) {
                            const {value} = context
                            //value解析，就是把组件的值转化为后台所需要的值
                            //在form表单点击保存按钮后，提交到后台之前执行转化
                            if (value) {
                                context.form.game_release_date_after = value[0]
                                context.form.game_release_date_before = value[1]
                            }
                            //  ↑↑↑↑↑ 注意这里是form，不是row
                        }
                    },
                    column: {
                        align: 'center',
                        sortable: true,
                        width: 150,
                    },
                    form: {
                        show: false
                    }
                }, our_ratio: {
                    title: "我方分成比例(%)",
                    type: "number",
                    search: {show: true},
                    form: {
                        rules: [{required: true, message: '请输入我方分成比例'}],
                        component: {props: {clearable: true}},
                    },
                    column: {
                        align: "center",
                        width: 150,
                    },
                }, channel_ratio: {
                    title: "渠道分成比例(%)",
                    type: "number",
                    search: {show: true},
                    form: {
                        rules: [{required: true, message: '请输入渠道分成比例'}],
                        component: {props: {clearable: true}},
                    },
                    column: {
                        align: "center",
                        width: 150,
                    },
                }, channel_fee_ratio: {
                    title: "渠道费比例(%)",
                    type: "number",
                    search: {show: true},
                    form: {
                        rules: [{required: true, message: '请输入渠道费比例'}],
                        component: {props: {clearable: true}},
                    },
                    column: {
                        align: "center",
                        width: 150,
                    },
                }, channel_tips: {
                    title: "分成备注",
                    type: "textarea",
                    column: {
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                ...commonCrudConfig()
            },
        },
    };
};
