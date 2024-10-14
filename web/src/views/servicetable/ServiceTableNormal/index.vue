<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #pagination-left>
        <el-tooltip content="打包下载">
          <el-button text type="primary" :disabled="selectedRowsCount === 0" :icon="Download" circle
                     @click="handleBatchDownload"/>
        </el-tooltip>
      </template>
      <template #pagination-right>
        <el-popover placement="top" :width="400" trigger="click">
          <template #reference>
            <el-button text :type="selectedRowsCount > 0 ? 'primary' : ''">已选中{{
                selectedRowsCount
              }}条数据
            </el-button>
          </template>
          <el-table :data="selectedRows" size="small">
            <el-table-column width="150" property="id" label="id"/>
            <el-table-column fixed="right" label="操作" min-width="60">
              <template #default="scope">
                <el-button text type="info" :icon="Close" @click="removeSelectedRows(scope.row)" circle/>
              </template>
            </el-table-column>
          </el-table>
        </el-popover>
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
import {Close, Delete, Download} from '@element-plus/icons-vue';
import {batchDownloadServiceTable} from "/@/views/servicetable/ServiceTableNormal/api";
import {errorMessage} from "/@/utils/message";
// 当前选择的菜单信息
let selectOptions: any = ref({name: null});

const {crudRef, crudBinding, crudExpose, context, selectedRows} = useFs({createCrudOptions, context: {selectOptions}});
const {doRefresh, setTableData} = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
  return selectedRows.value.length;
});

// 批量删除
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
  console.log(data);
  const response = await batchDownloadServiceTable(data);
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

// 移除已选中的行
const removeSelectedRows = (row: any) => {
  const tableRef = crudExpose.getBaseTableRef();
  const tableData = crudExpose.getTableData();
  if (XEUtils.pluck(tableData, 'id').includes(row.id)) {
    tableRef.toggleRowSelection(row, false);
  } else {
    selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== row.id);
  }
};
onMounted(() => {
  crudExpose.doRefresh();
});

defineExpose({selectOptions});
</script>