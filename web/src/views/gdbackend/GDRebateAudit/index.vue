<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #pagination-right>
				<el-popover placement="top" :width="400" trigger="click">
					<template #reference>
						<el-button text :type="selectedRowsCount > 0 ? 'primary' : ''">已选中{{ selectedRowsCount }}条数据</el-button>
					</template>
					<el-table :data="selectedRows" size="small">
						<el-table-column width="150" property="id" label="id" />
						<el-table-column fixed="right" label="操作" min-width="60">
							<template #default="scope">
								<el-button text type="info" :icon="Close" @click="removeSelectedRows(scope.row)" circle />
							</template>
						</el-table-column>
					</el-table>
				</el-popover>
			</template>
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="GDRebateAudit">
import { computed, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import XEUtils from 'xe-utils';
import { Close } from '@element-plus/icons-vue';

const { crudBinding, crudRef, crudExpose, selectedRows } = useFs({ createCrudOptions });
const selectedRowsCount = computed(() => selectedRows.value.length);
const removeSelectedRows = (row: any) => {
	const tableRef = crudExpose.getBaseTableRef();
	const tableData = crudExpose.getTableData();
	if (XEUtils.pluck(tableData, 'id').includes(row.id)) {
		tableRef.toggleRowSelection(row, false);
	} else {
		selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== row.id);
	}
};
// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>
