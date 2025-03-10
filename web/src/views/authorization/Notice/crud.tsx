// Notice CRUD TypeScript - Auto-generated on 2024-08-13 14:10:49

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
import {errorMessage, successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "../../../utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const lists = await api.GetList(query);
        lists.data.forEach((item: any) => {
            if (item.notice_filepath && item.notice_filepath.endsWith(".zip")) {

                const new_filepath = item.notice_filepath.split('/').pop();

                // 创建新的对象格式
                item.notice_filepath = {
                    id: item.id,
                    label: new_filepath,
                };
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

    const generateRequest = async (row: any) => {
        return await api.GenerateAuthorizationLetter(row.id);
    }

    const downloadRequest = async (row: any) => {
        return await api.DownloadAuthorizationLetter(row.id);
    }

    const clearRequest = async () => {
        return await api.ClearAuthorizationLetter();
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
                        show: auth("Notice:Create")
                    },
                    clear: {
                        show: auth("Notice:Clear"),
                        text: '清理文件',
                        type: 'info',
                        click: async () => {
                            const result = await clearRequest();
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
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("Notice:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("Notice:Delete")
                    },
                    generate: {
                        title: '生成',
                        text: '生成',
                        type: 'text',
                        iconRight: 'Upload',
                        show: auth("Notice:Generate"),
                        click: async (obj) => {
                            const result = await generateRequest(obj.row);
                            if (result.status) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.message}`);
                            }
                            await crudExpose?.doRefresh();
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
                }, title: {
                    title: "标题",
                    type: "text",
                    form: {show: false},
                    column: {
                        width: 160,
                    }
                }, game_names: {
                    title: "游戏",
                    type: "text",
                    column: {
                        showOverflowTooltip: true,
                        align: 'center',
                    },
                    form: {
                        show: false
                    }
                }, games: {
                    title: "游戏",
                    type: "dict-select",
                    dict: dict({
                        url: '/api/game_manage/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    }),
                    search: {
                        show: true,
                    },
                    column: {
                        // minWidth: 200,
                        // showOverflowTooltip: true
                        show: false
                    },
                    form: {
                        rules: [{
                            required: true,
                            message: '请选择游戏'
                        }],
                        component: {
                            multiple: true,
                            filterable: true,
                            placeholder: '请选择游戏',
                        }
                    }
                }, build_date: {
                    title: "公告日期",
                    type: "date",
                    form: {
                        component: {
                            pickerType: "date",
                            props: {
                                type: "date",
                                format: "YYYY-MM-DD",
                                "value-format": "YYYY-MM-DD",
                            }
                        }
                    }

                }, build_type: {
                    title: "公告类型",
                    type: "dict-select",
                    column: {
                        width: 100,
                    },
                    dict: dict({
                        data: [
                            {'label': '下架', 'value': 0},
                            {'label': '关服', 'value': 1}
                        ],
                        label: "label",
                        value: "value"
                    })
                }, notice_filepath: {
                    title: "公告文件路径",
                    type: "dict-select",
                    column: {
                        showOverflowTooltip: true,
                        align: 'center',
                        component: {
                            color: 'primary',
                            onClick: async (row: any) => {
                                if (auth("Notice:Download")) {
                                    const response = await downloadRequest(row.item);
                                    try {
                                        if (response.data) {
                                            if (response.headers['content-type'] === 'application/json') {
                                                const reader = new FileReader();
                                                reader.readAsText(response.data);
                                                reader.onload = function (e) {
                                                    const res = JSON.parse(reader.result as string);
                                                    errorMessage(`下载失败: ${res.message}`);
                                                }
                                            } else if (response.headers['content-type'] === 'application/zip') {
                                                const blob = new Blob([response.data], {type: response.headers['content-type']});
                                                const url = window.URL.createObjectURL(blob);
                                                const a = document.createElement('a');
                                                a.style.display = 'none';
                                                a.href = url;
                                                a.download = String(`${row.item.label}`.split('/').pop());
                                                document.body.appendChild(a);
                                                a.click();
                                                window.URL.revokeObjectURL(url);
                                                successMessage(`开始下载: ${row.item.label}`);
                                            }
                                        } else {
                                            errorMessage(`下载失败: ${response.message}`);
                                        }
                                    } catch (e) {
                                        errorMessage(`调用失败: ${e}`);

                                    }
                                } else {
                                    errorMessage("很抱歉，您没有下载权限");
                                }
                            }
                        }
                    },
                    form: {
                        show: false
                    },

                }, tips: {
                    title: "备注",
                    type: "input",
                    column: {
                        align: 'center',
                        show: false,
                    },
                    form: {
                        show: false
                    }

                }, status: {
                    title: "文件状态",
                    type: "dict-select",
                    column: {
                        width: 100,
                    },
                    dict: dict({
                        data: [
                            {'label': '未生成', 'value': 0},
                            {'label': '已生成', 'value': 1},
                            {'label': '正在生成', 'value': 2},
                            {'label': '生成失败', 'value': 3}
                        ],
                        label: "label",
                        value: "value"
                    }),
                    form: {
                        show: false
                    }
                },
                ...commonCrudConfig(
                    {
                        create_datetime: {
                            table: true,
                            search: true,
                        }
                    }
                )
            },
        },
    };

}