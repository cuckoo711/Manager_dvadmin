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
import {errorMessage, infoMessage, successMessage, warningMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'
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
    const generateServiceTable = async (row: any) => {
        return await api.generateServiceTable(row.id);
    }
    const downloadfirstRequest = async (row: any) => {
        return await api.DownloadFirst(row.id);
    }
    const downloadnofirstRequest = async (row: any) => {
        return await api.DownloadNoFirst(row.id);
    }

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
                    },
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 550,
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
                    generate: {
                        title: '生成',
                        text: '生成',
                        type: 'text',
                        iconRight: 'Upload',
                        show: auth("ServiceTableNormal:Generate"),
                        click: async (obj: any) => {
                            const result = await generateServiceTable(obj.row);
                            if (result.status) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.message}`);
                            }
                            await crudExpose?.doRefresh();
                        }
                    },
                    copy_content: {
                        title: '复制内容',
                        text: '复制内容',
                        type: 'text',
                        iconRight: 'DocumentCopy',
                        show: true,
                        click: async (obj: any) => {
                            if (obj.row.copy_content) {
                                navigator.clipboard.writeText(
                                    obj.row.copy_content
                                ).then(() => {
                                    successMessage('复制成功');
                                });
                            } else {
                                warningMessage('没有内容可以复制');
                            }
                        }
                    },
                    download_first: {
                        show: true,
                        text: '下载带首服表',
                        type: 'text',
                        iconRight: 'Download',
                        click: async (obj: any) => {
                            if (auth("ServiceTableNormal:DownloadFirst")) {
                                // noinspection TypeScriptUnresolvedReference
                                if ((obj.row.generate_status).toString() === '1') {
                                    successMessage(`开始下载, 请稍候（约10s内开始下载任务）`);
                                    const response = await downloadfirstRequest(obj.row);
                                    try {
                                        if (response.data) {
                                            if (response.headers['content-type'] === 'application/json') {
                                                const reader = new FileReader();
                                                reader.readAsText(response.data);
                                                reader.onload = function (e) {
                                                    const res = JSON.parse(reader.result as string);
                                                    errorMessage(`下载失败: ${res.message}`);
                                                }
                                            } else {
                                                const blob = new Blob([response.data], {type: response.headers['content-type']});
                                                const url = window.URL.createObjectURL(blob);
                                                const a = document.createElement('a');
                                                a.style.display = 'none';
                                                a.href = url;
                                                a.download = (obj.row.game_name).toString() + '_无首服.xlsx'
                                                ;  // 动态设置文件名
                                                document.body.appendChild(a);
                                                a.click();
                                                window.URL.revokeObjectURL(url);
                                            }
                                        } else {
                                            errorMessage(`下载失败: ${response.message}`);
                                        }
                                    } catch (e) {
                                        errorMessage(`调用失败: ${e}`);

                                    }
                                } else {
                                    warningMessage("当前任务状态不支持下载");
                                }
                            } else {
                                infoMessage("没有下载权限");
                            }
                        }
                    },
                    download_no_first: {
                        show: true,
                        text: '下载不带首服表',
                        type: 'text',
                        iconRight: 'Download',
                        click: async (obj: any) => {
                            if (auth("ServiceTableNormal:DownloadNoFirst")) {
                                if ((obj.row.generate_status).toString() === '1') {
                                    successMessage(`开始下载, 请稍候（约10s内开始下载任务）`);
                                    const response = await downloadnofirstRequest(obj.row);
                                    try {
                                        if (response.data) {
                                            if (response.headers['content-type'] === 'application/json') {
                                                const reader = new FileReader();
                                                reader.readAsText(response.data);
                                                reader.onload = function (e) {
                                                    const res = JSON.parse(reader.result as string);
                                                    errorMessage(`下载失败: ${res.message}`);
                                                }
                                            } else {
                                                const blob = new Blob([response.data], {type: response.headers['content-type']});
                                                const url = window.URL.createObjectURL(blob);
                                                const a = document.createElement('a');
                                                a.style.display = 'none';
                                                a.href = url;
                                                a.download = (obj.row.game_name).toString() + '.xlsx'
                                                ;  // 动态设置文件名
                                                document.body.appendChild(a);
                                                a.click();
                                                window.URL.revokeObjectURL(url);
                                            }
                                        } else {
                                            errorMessage(`下载失败: ${response.message}`);
                                        }
                                    } catch (e) {
                                        errorMessage(`调用失败: ${e}`);

                                    }
                                } else {
                                    warningMessage("当前任务状态不支持下载");
                                }
                            } else {
                                infoMessage("没有下载权限");
                            }
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
                }, game_name: {
                    title: "游戏名称",
                    type: "text",
                    search: {show: true},

                }, open_name: {
                    title: "初始区服名称",
                    type: "text",

                }, open_frequency: {
                    title: "开服频率",
                    type: "number",
                    column: {
                        align: 'center',
                    },

                }, open_count: {
                    title: "开服数量",
                    type: "number",
                    column: {
                        align: 'center',
                    },

                }, open_datetime: {
                    title: "开服时间",
                    type: "datetime",
                    column: {
                        align: 'center',
                        width: 240,
                    },
                    search: {
                        show: true,
                        col: {span: 8},
                        component: {
                            type: 'datetimerange',
                            props: {
                                'start-placeholder': '开始时间',
                                'end-placeholder': '结束时间',
                                'value-format': 'YYYY-MM-DD HH:mm:ss',
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
                            const {key, value} = context
                            //value解析，就是把组件的值转化为后台所需要的值
                            //在form表单点击保存按钮后，提交到后台之前执行转化
                            if (value) {
                                context.form.update_datetime_after = value[0]
                                context.form.update_datetime_before = value[1]
                            }
                            //  ↑↑↑↑↑ 注意这里是form，不是row
                        }
                    },

                }, copy_content: {
                    title: "复制内容",
                    type: "text",
                    form: {
                        show: false
                    },
                    column: {
                        show: false
                    },

                }, first_service_path: {
                    title: "首服文件路径",
                    type: "text",
                    form: {
                        show: false
                    },
                    column: {
                        show: false
                    },

                }, no_first_service_path: {
                    title: "无首服文件路径",
                    type: "text",
                    form: {
                        show: false
                    },
                    column: {
                        show: false
                    },

                }, generate_status: {
                    title: "生成状态",
                    type: "dict-select",
                    form: {
                        show: false
                    },
                    dict: dict({
                        data: [{'label': '未生成', 'value': '0'}, {'label': '已生成', 'value': '1'}],
                        label: "label",
                        value: "value"
                    })
                }, ...commonCrudConfig()
            },
        },
    };

}