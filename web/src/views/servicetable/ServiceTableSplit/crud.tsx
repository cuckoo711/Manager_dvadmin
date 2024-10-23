// ServiceTableSplit CRUD TypeScript - Auto-generated on 2024-10-16 10:26:09

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
        const lists = await api.GetList(query);
        lists.data.forEach((item: any) => {
            if (item.output_dir) {
                item.output_dir = item.output_dir.split('/').pop()
            }
            if (item.service_table_split_zip) {
                item.service_table_split_zip = item.service_table_split_zip.split('/').pop()
            }
        });
        return lists;
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
    const downloadSplitZip = async (row: any) => {
        return await api.DownloadSplitZip(row.id);
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
                show: false,
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("ServiceTableSplit:Delete")
                    },
                    generate: {
                        title: '生成',
                        text: '生成',
                        type: 'text',
                        iconRight: 'Upload',
                        show: auth("ServiceTableSplit:Generate"),
                        click: async (obj: any) => {
                            const result = await generateServiceTable(obj.row);
                            if (result.message) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.error}`);
                            }
                            await crudExpose?.doRefresh();
                        }
                    },
                    download_zip: {
                        show: true,
                        text: '下载',
                        type: 'text',
                        iconRight: 'Download',
                        click: async (obj: any) => {
                            if (auth("ServiceTableSplit:DownloadSplitZip")) {
                                // noinspection TypeScriptUnresolvedReference
                                if ((obj.row.generate_status).toString() === '1') {
                                    successMessage(`开始下载, 请稍候（约10s内开始下载任务）`);
                                    const response = await downloadSplitZip(obj.row);
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
                                                a.download = (obj.row.create_datetime).toString() + '开服表.zip'
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
                }, output_dir: {
                    title: "输出目录",
                    type: "text",
                }, service_table_split_zip: {
                    title: "分表压缩包路径",
                    type: "text",

                }, generate_status: {
                    title: "生成状态",
                    type: "dict-select",
                    dict: dict({
                        data: [{'label': '未生成', 'value': '0'}, {'label': '已生成', 'value': '1'},
                            {'label': '生成失败', 'value': '2'}, {'label': '生成中', 'value': '3'}],
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        width: 200
                    }

                },
                ...commonCrudConfig({
                    create_datetime: {table: true, search:true},
                })
            },
        },
    };

}