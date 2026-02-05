import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, CrudExpose, CreateCrudOptionsProps, CreateCrudOptionsRet, compute } from '@fast-crud/fast-crud';
import { auth } from '/@/utils/authFunction';
import { errorMessage, successMessage } from '/@/utils/message';
import XEUtils from 'xe-utils';
import { nextTick, ref } from 'vue';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  const selectedRows = ref<any[]>([]);

  const onSelectionChange = (rows: any[]) => {
    selectedRows.value = rows;
  };

  const toggleRowSelection = () => {
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

  const pageRequest = async (query: UserPageQuery) => {
    return await api.GetList(query);
  };
  const addRequest = async ({ form }: AddReq) => {
    return await api.AddObj(form);
  };
  const editRequest = async ({ form, row }: EditReq) => {
    form.id = row.id;
    return await api.UpdateObj(form);
  };
  const delRequest = async ({ row }: DelReq) => {
    return await api.DelObj(row.id);
  };

  const handleBatchApprove = async () => {
    const ids = XEUtils.pluck(selectedRows.value.filter((r: any) => r.status !== 3), 'id');
    if (ids.length === 0) {
      errorMessage('请选择可操作的记录');
      return;
    }
    const res = await api.BatchApprove(ids);
    if (res.status === 2000) {
      successMessage('批量允许发放成功');
      await crudExpose.doRefresh();
    }
  };
  const handleBatchCancel = async () => {
    const ids = XEUtils.pluck(selectedRows.value.filter((r: any) => r.status !== 3), 'id');
    if (ids.length === 0) {
      errorMessage('请选择可操作的记录');
      return;
    }
    const res = await api.BatchCancel(ids);
    if (res.status === 2000) {
      successMessage('批量取消发放成功');
      await crudExpose.doRefresh();
    }
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
						show: false,
					},
					batchApprove: {
						show: auth('GDRebateAudit:BatchApprove'),
						text: '批量允许发放',
						type: 'primary',
						click: handleBatchApprove,
					},
					batchCancel: {
						show: auth('GDRebateAudit:BatchCancel'),
						text: '批量取消发放',
						type: 'danger',
						click: handleBatchCancel,
					},
					batchIssue: {
						show: auth('GDRebateAudit:BatchIssue'),
						text: '批量发放',
						type: 'success',
						click: async () => {
							const ids = XEUtils.pluck(
								selectedRows.value.filter((r: any) => r.status === 1),
								'id'
							);
							if (ids.length === 0) {
								errorMessage('请选择允许发放状态的记录');
								return;
							}
							const res = await api.BatchIssue(ids);
              if (res.status === 2000) {
								successMessage('批量发放成功');
								await crudExpose.doRefresh();
							}
						},
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 220,
				buttons: {
					view: {
						show: auth('GDRebateAudit:Retrieve'),
						type: 'text',
						text: '详情',
					},
					edit: {
						type: 'text',
						show: false
					},
					approve: {
						show: compute((ctx: any) => {
							return auth('GDRebateAudit:Approve') && ctx.row.status === 0;
						}),
						type: 'text',
						text: '允许发放',
						click: async (ctx: any) => {
							const res = await api.Approve(ctx.row.id);
              if (res.status === 2000) {
								successMessage('已允许发放');
								await crudExpose.doRefresh();
							}
						},
					},
					cancel: {
						show: compute((ctx: any) => {
							return auth('GDRebateAudit:Cancel') && ctx.row.status !== 3;
						}),
						type: 'text',
						text: '取消发放',
						click: async (ctx: any) => {
							const res = await api.Cancel(ctx.row.id);
              if (res.status === 2000) {
								successMessage('已取消发放');
								await crudExpose.doRefresh();
							}
						},
					},
					issue: {
						show: compute((ctx: any) => {
							return auth('GDRebateAudit:Issue') && ctx.row.status === 1;
						}),
						type: 'text',
						text: '发放',
						click: async (ctx: any) => {
							const res = await api.Issue(ctx.row.id);
              if (res.status === 2000) {
								successMessage('发放成功');
								await crudExpose.doRefresh();
							}
						},
					},
					remove: {
						type: "text",
						show: compute((ctx: any) => {
							return auth('GDRebateAudit:Delete') && ctx.row.status !== 3;
						}),
					},
				},
			},
			table: {
				rowKey: 'id',
				onSelectionChange,
				onRefreshed: () => toggleRowSelection(),
			},
			form: {
				col: { span: 24 },
				labelWidth: '110px',
				wrapper: {
					is: 'el-dialog',
					width: '700px',
				},
			},
			columns: {
				$checked: {
					title: '选择',
					form: { show: false },
					column: {
						type: 'selection',
						align: 'center',
						width: '60px',
						selectable: (row: any) => row.status !== 3,
						columnSetDisabled: true,
					},
				},
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true,
					},
				},
				game_server_name: {
					title: '游戏名称',
					type: 'text',
					column: {
						align: 'center',
						width: 200,
					},
					form: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				role_info: {
					title: '角色信息',
					type: 'text',
					column: { align: 'center', width: 280, showOverflowTooltip: true },
					form: { show: false },
					search: { show: false },
				},
				serverid: {
					title: '角色区服',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				pid: {
					title: '角色ID',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				pname: {
					title: '角色名',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				mail_info: {
					title: '邮件信息',
					type: 'text',
					form: { show: false },
					column: { align: 'center', minWidth: 320, showOverflowTooltip: true },
					search: { show: false },
				},
				gifts_name: {
					title: '邮件标题',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				des: {
					title: '邮件内容',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				gift_info: {
					title: '礼包信息',
					type: 'text',
					form: { show: false },
					column: { align: 'center', width: 220, showOverflowTooltip: true },
					search: { show: false },
				},
				gift_label: {
					title: '礼包信息',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				gifts_id: {
					title: '礼包ID',
					type: 'text',
					form: { show: false },
					column: { show: false },
					search: { show: true, component: { props: { clearable: true } } },
				},
				status: {
					title: '审核状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 0, label: '待审核' },
							{ value: 1, label: '允许发放' },
							{ value: 2, label: '已取消' },
							{ value: 3, label: '已发放' },
						],
					}),
					column: { align: 'center', width: 120 },
				},
				issued_time_text: {
					title: '发放时间',
					type: 'text',
					form: { show: false },
					column: { align: 'center', width: 180 },
				},
				issued: {
					title: '是否已发放',
					type: 'dict-select',
					form: { show: false },
					column: { show: false },
					search: {
						show: true,
						component: { props: { clearable: true } },
					},
					dict: dict({
						data: [
							{ value: '', label: '全部' },
							{ value: '1', label: '是' },
							{ value: '0', label: '否' },
						],
					}),
				},
				description: {
					title: '备注',
					type: 'textarea',
					column: { show: false },
				},
			},
		},
	};
};
