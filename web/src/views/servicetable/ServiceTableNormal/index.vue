<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #pagination-left>
        <el-tooltip content="批量生成开服表">
          <el-button type="primary" :disabled="selectedRowsCount === 0" :icon="FolderAdd"
                     @click="handleBatchGenerate">
            批量生成开服表
          </el-button>
        </el-tooltip>
        <el-tooltip content="打包下载">
          <el-button type="primary" :disabled="selectedRowsCount === 0" :icon="Download"
                     @click="handleBatchDownload">
            打包下载
          </el-button>
        </el-tooltip>
      </template>
      <template #pagination-right>
        <el-tooltip :content="'已选中' + selectedRowsCount + '条数据'">
          <el-button type="primary" :disabled="selectedRowsCount === 0" :icon="BrushFilled"
                     @click="handleBatchSplitTask">
            创建分表任务
          </el-button>
        </el-tooltip>
      </template>
    </fs-crud>
  </fs-page>
</template>

<script lang="ts" setup name="ServiceTableNormal ">
// ServiceTableNormal Page - Auto-generated on 2024-10-11 09:43:03
import {computed, onMounted, ref} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {ElMessage, ElMessageBox} from 'element-plus';
import XEUtils from 'xe-utils';
import {BrushFilled, Download, FolderAdd} from '@element-plus/icons-vue';
import {
  batchDownloadServiceTable,
  batchGenerateServiceTable,
  batchSplitTaskServiceTable
} from "/@/views/servicetable/ServiceTableNormal/api";
import {errorMessage} from "/@/utils/message";
// 当前选择的菜单信息
let selectOptions: any = ref({name: null});

const {crudRef, crudBinding, crudExpose, selectedRows} = useFs({createCrudOptions, context: {selectOptions}});

// 选中行的条数
const selectedRowsCount = computed(() => {
  return selectedRows.value.length;
});

const handleBatchGenerate = async () => {
  await ElMessageBox.confirm(`确定要生成这${selectedRows.value.length}条记录的开服表吗`, '确认', {
    distinguishCancelAndClose: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    closeOnClickModal: false,
  });
  const data = {
    ids: XEUtils.pluck(selectedRows.value, 'id')
  }
  try {
    const response = await batchGenerateServiceTable(data);
    ElMessage.success('已提交生成开服表任务' + response.message);
  } catch (e) {
    errorMessage(`调用失败: ${e}`);
  }
  await crudExpose.doRefresh();
};

const handleBatchDownload = async () => {
  await ElMessageBox.confirm(`确定要批量下载这${selectedRows.value.length}条记录吗`, '确认', {
    distinguishCancelAndClose: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    closeOnClickModal: false,
  });
  const data = {
    ids: XEUtils.pluck(selectedRows.value, 'id')
  }
  // console.log(data);
  const response = await batchDownloadServiceTable(data);
  try {
    if (response.data) {
      if (response.headers['content-type'] === 'application/json') {
        const reader = new FileReader();
        reader.readAsText(response.data);
        reader.onload = function () {
          const res = JSON.parse(reader.result as string);
          errorMessage(`下载失败: ${res.message}`);
        }
      } else {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.download = '开服表.zip';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }
    } else {
      errorMessage(`下载失败: ${response.message}`);
    }
  } catch (e) {
    errorMessage(`调用失败: ${e}`);
  }
  await crudExpose.doRefresh();
};

const handleBatchSplitTask = async () => {
  await ElMessageBox.confirm(`确定要创建这${selectedRows.value.length}条记录的分表任务吗`, '确认', {
    distinguishCancelAndClose: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    closeOnClickModal: false,
  });
  const data = {
    ids: XEUtils.pluck(selectedRows.value, 'id')
  }
  try {
    const response = await batchSplitTaskServiceTable(data);
    ElMessage.success('已提交分表任务' + response.message);
  } catch (e) {
    errorMessage(`调用失败: ${e}`);
  }
  await crudExpose.doRefresh();
};

onMounted(() => {
  crudExpose.doRefresh();
});

defineExpose({selectOptions});
</script>