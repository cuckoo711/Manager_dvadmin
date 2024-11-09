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
import {nextTick, ref} from "vue";
import XEUtils from "xe-utils";
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
    const ClearServerTable = async () => {
        return await api.ClearServerTable();
    }
    // 记录选中的行
    const selectedRows = ref<any>([]);

    const onSelectionChange = (changed: any) => {
        const tableData = crudExpose.getTableData();
        const unChanged = tableData.filter((row: any) => !changed.includes(row));
        // 添加已选择的行
        XEUtils.arrayEach(changed, (item: any) => {
            const ids = XEUtils.pluck(selectedRows.value, 'id');
            if (!ids.includes(item.id)) {
                selectedRows.value = XEUtils.union(selectedRows.value, [item]);
            }
        });
        // 剔除未选择的行
        XEUtils.arrayEach(unChanged, (unItem: any) => {
            selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== unItem.id);
        });
    };
    const toggleRowSelection = () => {
        // 多选后，回显默认勾选
        const tableRef = crudExpose.getBaseTableRef();
        const tableData = crudExpose.getTableData();
        const selected = XEUtils.filter(tableData, (item: any) => {
            const ids = XEUtils.pluck(selectedRows.value, 'id');
            return ids.includes(item.id);
        });

        nextTick(() => {
            XEUtils.arrayEach(selected, (item) => {
                tableRef.toggleRowSelection(item, true);
            });
        });
    };

    return {
        selectedRows,
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
                    clear: {
                        show: auth("AuthorizationLetter:Clear"),
                        text: '清理文件',
                        type: 'info',
                        click: async () => {
                            const result = await api.ClearServerTable();
                            if (result.status) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.message}`);
                            }
                            await crudExpose?.doRefresh();
                        }
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 300,
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
                            if (result.message) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.error}`);
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
            table: {
                rowKey: 'id', //设置你的主键id， 默认rowKey=id
                onSelectionChange,
                onRefreshed: () => toggleRowSelection(),
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
                $checked: {
                    title: '选择',
                    form: {show: false},
                    column: {
                        type: 'selection',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                    },
                },
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
                    column: {
                        align: 'center',
                        width: 300,
                    },

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

                }, create_datetime: {}, generate_status: {
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
                }, ...commonCrudConfig({
                    create_datetime: {table: true, search: true},
                })
            },
        },
    };

}