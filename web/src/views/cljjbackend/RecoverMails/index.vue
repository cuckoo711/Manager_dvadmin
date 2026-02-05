<template>
  <div class="canglan-recover-mails">
    <fs-page>
      <el-main style="display: flex; flex-direction: column; height: 100%">
        <el-form inline label-width="auto" label-position="top" style="width: 100%">
          <el-row :gutter="20" style="width: 100%">
            <el-col :span="6">
              <el-form-item label="游戏服">
                <el-select v-model="serverId" placeholder="请选择游戏服" filterable>
                  <el-option
                    v-for="item in serverList"
                    :key="item.id"
                    :label="item.gamename"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="角色ID">
                <el-input v-model="userId" placeholder="输入角色ID" />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="操作">
                <el-button type="primary" @click="onQueryBackups">查询备份</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <div style="margin-top: 10px">备份列表</div>
        <div ref="tableWrapRef" style="flex: 1; min-height: 0">
          <el-table-v2
            :data="backupList"
            :columns="backupColumns"
            :width="containerWidth"
            :height="containerHeight"
            fixed
          />
        </div>
        <div style="margin-top: 10px; text-align: right">
          <el-tooltip :disabled="!recoverDisabled" content="请先勾选要恢复的备份" placement="top">
            <el-button type="success" :disabled="recoverDisabled" @click="onRecoverBackups">恢复备份</el-button>
          </el-tooltip>
        </div>
      </el-main>
    </fs-page>
    <el-dialog v-model="loading" width="30%" :show-close="false">
      <div style="text-align: center">正在处理</div>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, h, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElCheckbox, ElTooltip } from 'element-plus';
import { MailBackups, RecoverMailBackups, GetServers } from './api';

const loading = ref(false);
const serverId = ref('');
const serverList = ref<any[]>([]);
const userId = ref('');
const backupList = ref<any[]>([]);
const selectedIds = ref<Set<string>>(new Set());
const recoverDisabled = computed(() => selectedIds.value.size === 0);
const tableWrapRef = ref<HTMLElement | null>(null);
const containerWidth = ref(0);
const containerHeight = ref(0);
let resizeObs: ResizeObserver | null = null;

const fetchServers = async () => {
  try {
    const res = await GetServers();
    serverList.value = res.data || [];
    if (serverList.value.length > 0) {
      serverId.value = serverList.value[0].id;
    }
  } catch (e) {
    ElMessage.error('获取游戏服列表失败');
  }
};

onMounted(() => {
  fetchServers();
  const el = tableWrapRef.value;
  if (!el) return;
  resizeObs = new ResizeObserver((entries) => {
    const cr = entries[0].contentRect;
    containerWidth.value = Math.floor(cr.width);
    containerHeight.value = Math.floor(cr.height);
  });
  resizeObs.observe(el);
});
onUnmounted(() => {
  resizeObs && resizeObs.disconnect();
  resizeObs = null;
});
const toggleRow = (row: any, val: boolean) => {
  const id = String(row?.backup_id || '').trim();
  if (!id) return;
  if (val) {
    selectedIds.value.add(id);
  } else {
    selectedIds.value.delete(id);
  }
};
const canvasEl = document.createElement('canvas');
const ctx = canvasEl.getContext('2d');
const measureText = (text: any, font = '14px Arial') => {
  if (!ctx) return 100;
  ctx.font = font;
  const s = String(text ?? '');
  const m = ctx.measureText(s);
  return Math.ceil(m.width) + 28;
};
const computeWidths = (data: any[], labels: Record<string, string>, limits: Record<string, { min: number; max: number }>, extraSpace = 0) => {
  const keys = Object.keys(labels);
  const res: Record<string, number> = {};
  keys.forEach(k => {
    const headerW = measureText(labels[k]);
    let maxW = headerW;
    for (let i = 0; i < Math.min(data.length, 200); i++) {
      maxW = Math.max(maxW, measureText(data[i]?.[k]));
    }
    const lim = limits[k] || { min: 100, max: 400 };
    res[k] = Math.max(lim.min, Math.min(lim.max, maxW));
  });
  const total = Object.values(res).reduce((a, b) => a + b, 0) + extraSpace;
  const avail = Math.max(containerWidth.value - 20, 600);
  if (total < avail) {
    const ratio = (avail - extraSpace) / (total - extraSpace);
    Object.keys(res).forEach(k => {
      const lim = limits[k] || { min: 100, max: 400 };
      res[k] = Math.max(lim.min, Math.min(lim.max, Math.floor(res[k] * ratio)));
    });
  }
  return res;
};
const backupColumns = computed(() => {
  const selectWidth = 80;
  const labels = {
    backup_id: '备份ID',
    user_id: '角色ID',
    mail_id: '邮件ID',
    mail_type: '类型',
    msg_type: '消息类型',
    item_count: '附件数量',
    limit_type: '限制类型',
    delete_time: '删除时间'
  } as Record<string, string>;
  const limits = {
    backup_id: { min: 140, max: 220 },
    user_id: { min: 140, max: 240 },
    mail_id: { min: 160, max: 260 },
    mail_type: { min: 120, max: 160 },
    msg_type: { min: 140, max: 220 },
    item_count: { min: 120, max: 160 },
    limit_type: { min: 140, max: 220 },
    delete_time: { min: 160, max: 240 }
  } as Record<string, { min: number; max: number }>;
  const widths = computeWidths(backupList.value || [], labels, limits, selectWidth);
  const total = backupList.value?.length || 0;
  const allChecked = total > 0 && selectedIds.value.size === total;
  const indeterminate = selectedIds.value.size > 0 && selectedIds.value.size < total;
  return [
    {
      key: 'select',
      title: '选择',
      dataKey: 'select',
      width: selectWidth,
      headerCellRenderer: () =>
        h(ElCheckbox, {
          modelValue: allChecked,
          indeterminate: indeterminate,
          'onUpdate:modelValue': (val: any) => {
            if (val) {
              const ids = (backupList.value || []).map(r => String(r?.backup_id || '')).filter(Boolean);
              selectedIds.value = new Set(ids);
            } else {
              selectedIds.value.clear();
            }
          }
        }),
      cellRenderer: ({ rowData }: any) =>
        h(ElCheckbox, {
          modelValue: selectedIds.value.has(String(rowData?.backup_id || '')),
          'onUpdate:modelValue': (val: any) => toggleRow(rowData, Boolean(val))
        })
    },
    { key: 'backup_id', title: labels.backup_id, dataKey: 'backup_id', width: widths.backup_id },
    { key: 'user_id', title: labels.user_id, dataKey: 'user_id', width: widths.user_id },
    { key: 'mail_id', title: labels.mail_id, dataKey: 'mail_id', width: widths.mail_id },
    { key: 'mail_type', title: labels.mail_type, dataKey: 'mail_type', width: widths.mail_type },
    { key: 'msg_type', title: labels.msg_type, dataKey: 'msg_type', width: widths.msg_type },
    { key: 'item_count', title: labels.item_count, dataKey: 'item_count', width: widths.item_count },
    { key: 'limit_type', title: labels.limit_type, dataKey: 'limit_type', width: widths.limit_type },
    { key: 'delete_time', title: labels.delete_time, dataKey: 'delete_time', width: widths.delete_time }
  ];
});

const parseIdsInput = (v: string) => {
  const s = v.split(/[\n,]+/).map(i => i.trim()).filter(Boolean);
  return s;
};

const toArray = (x: any) => {
  if (Array.isArray(x)) return x;
  if (typeof x === 'string') {
    try {
      const y = JSON.parse(x);
      return Array.isArray(y) ? y : [];
    } catch {
      return [];
    }
  }
  return [];
};

const formatMailInfo = (arr: any[]) => {
  return {
    mail_type: arr[0],
    msg_type: arr[1],
    item_count: Array.isArray(arr[2]) ? arr[2].length : 0,
    source_type: arr[3],
    is_new: arr[4],
    limit_type: arr[5],
    is_locked: arr[6],
    ext: typeof arr[7] === 'object' ? JSON.stringify(arr[7]) : String(arr[7] ?? '')
  };
};

const onQueryBackups = async () => {
  if (!serverId.value) {
    ElMessage.warning('请选择游戏服');
    return;
  }
  if (!userId.value) {
    ElMessage.warning('请输入角色ID');
    return;
  }
  loading.value = true;
  try {
    const res = await MailBackups(serverId.value, userId.value);
    const raw = res.data || [];
    backupList.value = raw.map((it: any) => {
      const info = formatMailInfo(toArray(it?.mail_info));
      return { ...it, ...info };
    });
    selectedIds.value.clear();
  } catch {
    ElMessage.error('查询失败');
  } finally {
    loading.value = false;
  }
};

const onRecoverBackups = async () => {
  if (!serverId.value) {
    ElMessage.warning('请选择游戏服');
    return;
  }
  if (!userId.value) {
    ElMessage.warning('请输入角色ID');
    return;
  }
  const ids = Array.from(selectedIds.value);
  if (!ids.length) {
    ElMessage.warning('请输入备份ID列表');
    return;
  }
  loading.value = true;
  try {
    const res = await RecoverMailBackups(serverId.value, userId.value, ids);
    ElMessage.success('恢复完成');
    await onQueryBackups();
  } catch {
    ElMessage.error('恢复失败');
  } finally {
    loading.value = false;
  }
};
</script>
