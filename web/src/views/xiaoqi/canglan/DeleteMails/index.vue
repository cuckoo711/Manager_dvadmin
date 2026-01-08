<template>
  <div class="canglan-delete-mails">
    <fs-page>
      <el-main style="display: flex; flex-direction: column; height: 100%">
        <el-form inline label-width="auto" label-position="top" style="width: 100%">
          <el-row :gutter="20" style="width: 100%">
            <el-col :span="8">
              <el-form-item label="角色ID">
                <el-input v-model="uid" placeholder="输入角色ID" />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="操作">
                <el-button type="primary" @click="onSearchUser">查询用户与邮件</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <el-card shadow="never" style="margin-top: 10px">
          <div style="margin-bottom: 10px">用户信息</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">{{ searchResult.userinfo.userid }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ searchResult.userinfo.username }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <div ref="tableWrapRef" style="flex: 1; min-height: 0; margin-top: 10px">
          <el-table-v2
            :data="searchResult.usermails"
            :columns="mailColumns"
            :width="containerWidth"
            :height="containerHeight"
            fixed
          />
        </div>
        <div style="margin-top: 10px; text-align: right">
          <el-tooltip :disabled="!deleteDisabled" content="请先勾选要删除的邮件" placement="top">
            <el-button type="danger" :disabled="deleteDisabled" @click="onDeleteMails">删除邮件</el-button>
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
import { ref, computed, onMounted, onUnmounted, h } from 'vue';
import { ElMessage, ElCheckbox, ElTooltip } from 'element-plus';
import { SearchUserInfo, DeleteMails } from './api';

const loading = ref(false);
const uid = ref('');
const searchResult = ref<{ userinfo: any; usermails: any[] }>({ userinfo: {}, usermails: [] });
const selectedMailIds = ref<Set<string>>(new Set());
const deleteDisabled = computed(() => selectedMailIds.value.size === 0);

const tableWrapRef = ref<HTMLElement | null>(null);
const containerWidth = ref(0);
const containerHeight = ref(0);
let resizeObs: ResizeObserver | null = null;
onMounted(() => {
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
const mailColumns = computed(() => {
  const selectWidth = 80;
  const labels = {
    mail_id: '邮件ID',
    mail_type: '类型',
    msg_type: '消息类型',
    item_list: '附件',
    source_type: '来源类型',
    is_new: '是否新',
    limit_type: '限制类型',
    is_locked: '是否锁定'
  } as Record<string, string>;
  const limits = {
    mail_id: { min: 140, max: 220 },
    mail_type: { min: 110, max: 160 },
    msg_type: { min: 140, max: 220 },
    item_list: { min: 200, max: 700 },
    source_type: { min: 140, max: 220 },
    is_new: { min: 110, max: 160 },
    limit_type: { min: 140, max: 220 },
    is_locked: { min: 120, max: 180 }
  } as Record<string, { min: number; max: number }>;
  const widths = computeWidths(searchResult.value.usermails || [], labels, limits, selectWidth);
  const total = searchResult.value.usermails?.length || 0;
  const allChecked = total > 0 && selectedMailIds.value.size === total;
  const indeterminate = selectedMailIds.value.size > 0 && selectedMailIds.value.size < total;
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
              const ids = (searchResult.value.usermails || []).map(r => String(r?.mail_id || '')).filter(Boolean);
              selectedMailIds.value = new Set(ids);
            } else {
              selectedMailIds.value.clear();
            }
          }
        }),
      cellRenderer: ({ rowData }: any) =>
        h(ElCheckbox, {
          modelValue: selectedMailIds.value.has(String(rowData?.mail_id || '')),
          'onUpdate:modelValue': (val: any) => {
            const id = String(rowData?.mail_id || '').trim();
            if (!id) return;
            if (Boolean(val)) {
              selectedMailIds.value.add(id);
            } else {
              selectedMailIds.value.delete(id);
            }
          }
        })
    },
    { key: 'mail_id', title: labels.mail_id, dataKey: 'mail_id', width: widths.mail_id },
    { key: 'mail_type', title: labels.mail_type, dataKey: 'mail_type', width: widths.mail_type },
    { key: 'msg_type', title: labels.msg_type, dataKey: 'msg_type', width: widths.msg_type },
    { key: 'item_list', title: labels.item_list, dataKey: 'item_list', width: widths.item_list },
    { key: 'source_type', title: labels.source_type, dataKey: 'source_type', width: widths.source_type },
    { key: 'is_new', title: labels.is_new, dataKey: 'is_new', width: widths.is_new },
    { key: 'limit_type', title: labels.limit_type, dataKey: 'limit_type', width: widths.limit_type },
    { key: 'is_locked', title: labels.is_locked, dataKey: 'is_locked', width: widths.is_locked }
  ];
});

const parseIdsInput = (v: string) => {
  const s = v.split(/[\n,]+/).map(i => i.trim()).filter(Boolean);
  return s;
};

const onSearchUser = async () => {
  if (!uid.value) {
    ElMessage.warning('请输入角色ID');
    return;
  }
  loading.value = true;
  try {
    const res = await SearchUserInfo(uid.value);
    searchResult.value = res.data || { userinfo: {}, usermails: [] };
    selectedMailIds.value.clear();
  } catch {
    ElMessage.error('查询失败');
  } finally {
    loading.value = false;
  }
};

const onDeleteMails = async () => {
  if (!uid.value) {
    ElMessage.warning('请输入角色ID');
    return;
  }
  const finalIds = Array.from(selectedMailIds.value);
  if (!finalIds.length) {
    ElMessage.warning('请先勾选要删除的邮件');
    return;
  }
  loading.value = true;
  try {
    const res = await DeleteMails(uid.value, finalIds);
    ElMessage.success('删除完成');
    await onSearchUser();
  } catch {
    ElMessage.error('删除失败');
  } finally {
    loading.value = false;
  }
};
</script>
