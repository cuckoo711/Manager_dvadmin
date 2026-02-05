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
    if (res.code === 2000) {
      successMessage('批量允许发放成功');
      crudExpose.doRefresh();
    }
  };
  const handleBatchCancel = async () => {
    const ids = XEUtils.pluck(selectedRows.value.filter((r: any) => r.status !== 3), 'id');
    if (ids.length === 0) {
      errorMessage('请选择可操作的记录');
      return;
    }
    const res = await api.BatchCancel(ids);
    if (res.code === 2000) {
      successMessage('批量取消发放成功');
      crudExpose.doRefresh();
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
            show: auth('GDRebateAudit:Create'),
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
              const ids = XEUtils.pluck(selectedRows.value.filter((r: any) => r.status === 1), 'id');
              if (ids.length === 0) {
                errorMessage('请选择允许发放状态的记录');
                return;
              }
              const res = await api.BatchIssue(ids);
              if (res.code === 2000) {
                successMessage('批量发放成功');
                crudExpose.doRefresh();
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
          approve: {
            show: compute((ctx: any) => {
              return auth('GDRebateAudit:Approve') && ctx.row.status === 0;
            }),
            type: 'text',
            text: '允许发放',
            click: async (ctx: any) => {
              const res = await api.Approve(ctx.row.id);
              if (res.code === 2000) {
                successMessage('已允许发放');
                crudExpose.doRefresh();
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
              if (res.code === 2000) {
                successMessage('已取消发放');
                crudExpose.doRefresh();
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
              if (res.code === 2000) {
                successMessage('发放成功');
                crudExpose.doRefresh();
              }
            },
          },
          remove: {
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
        game_server: {
          title: '游戏',
          type: 'dict-select',
          search: { show: true },
          dict: dict({
            url: '/api/GDServer/?page=1&limit=99999',
            value: 'id',
            label: 'gamename',
          }),
          form: {
            rules: [{ required: true, message: '请选择游戏' }],
          },
          column: {
            show: false,
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
        },
        serverid: {
          title: '服务器ID',
          type: 'text',
          search: { show: true },
          form: {
            rules: [{ required: true, message: '请输入服务器ID' }],
          },
          column: { align: 'center', width: 120 },
        },
        pid: {
          title: '角色ID',
          type: 'text',
          search: { show: true },
          form: {
            rules: [{ required: true, message: '请输入角色ID' }],
          },
          column: { align: 'center', width: 120 },
        },
        pname: {
          title: '角色名称',
          type: 'text',
          search: { show: true },
          column: { align: 'center', width: 200, showOverflowTooltip: true },
        },
        amount: {
          title: '返利金额',
          type: 'number',
          column: { align: 'center', width: 120 },
          form: {
            rules: [{ required: true, message: '请输入返利金额' }],
          },
        },
        reason: {
          title: '返利原因',
          type: 'textarea',
          column: { align: 'center', width: 280, showOverflowTooltip: true },
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
        issued_time: {
          title: '发放时间',
          type: 'datetime',
          form: { show: false },
          column: { align: 'center', width: 180 },
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
