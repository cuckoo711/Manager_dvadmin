import { CreateCrudOptionsProps, CreateCrudOptionsRet, AddReq, DelReq, EditReq, dict, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { dictionary } from '/@/utils/dictionary';
import { auth } from '/@/utils/authFunction';
import { nextTick, computed } from 'vue';

/**
 *
 * @param crudExpose：index传递过来的示例
 * @param context：index传递过来的自定义参数
 * @returns
 */
export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
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
			pagination: {
				show: true,
			},
			  table: {
				show: false,
			  },
			  toolbar: {
				compact: false
			  },
			actionbar: {
				buttons: {
					add: {
						show: auth('role:Create'),
					},
				},
			},
			rowHandle: {
				align: "center",
				//固定右侧
				fixed: 'right',
				width: computed(() => {
					if (auth('role:AuthorizedAdd') || auth('role:AuthorizedSearch')) {
						return 420;
					}
					return 320;
				}),
				buttons: {
					view: {
						show: true,
					},
					edit: {
						show: auth('role:Update'),
					},
					remove: {
						show: auth('role:Delete'),
					},
				},
			},
			form: {
				col: { span: 24 },
				labelWidth: '100px',
				wrapper: {
					is: 'el-dialog',
					width: '900px',
				},
			},
			columns: {
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
					},
				},
				id: {
					title: 'ID',
					column: { show: false },
					search: { show: false },
					form: { show: false },
				},
				name: {
					title: '任务名称',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '任务名称必填' }],
						component: {
							placeholder: '请输入任务名称',
						},
					},
				},
				task: {
					title: '执行任务',
					type: 'dict-select',
					dict: dict({
						url: '/api/dvadmin_celery/task/job_list/?limit=999',
						value: 'label',
						label: 'label',
					}),
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						columnSetDisabled: true,
					},
					form: {
						rules: [{ required: true, message: '执行任务必填' }],
						component: {
							placeholder: '输入执行任务',
						},
					},
					valueBuilder(context) {
						const { row, key } = context;
						return row[key];
					},
				},
				last_run_at: {
					title: '最后运行时间',
					search: { show: false },
					type: ' datetime',
					form: {
						show: false,
						rules: [{ required: true, message: '最后运行时间必填' }],
					},
				},
				description: {
					title: '备注',
					search: { show: false },
					type: ' datetime',
					form: {
						show: false,
						rules: [{ required: true, message: '备注必填' }],
					},
				},
				cron: {
					title: '表达式',
					search: { show: false },
					type: 'number',
					column: {
						minWidth: 90,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '表达式必填' }],
						value: '1-15 1 * * *',
					},
				},
				kwargs: {
					title: '请求参数',
					search: { show: false },
					type: 'text',
					column: {
						minWidth: 90,
						sortable: 'custom',
					}
				},
				enabled: {
					title: '状态',
					search: { show: true },
					type: 'dict-radio',
					form: {
						rules: [{ required: true, message: '排序必填' }],
						value: true,
					},
					dict: dict({
						data: [
							{
								label: '启用',
								value: true,
								color: 'success',
								effect: 'dark',
							},
							{
								label: '禁用',
								value: false,
								effect: 'dark',
							},
						],
					}),
				},
			},
		},
	};
};
