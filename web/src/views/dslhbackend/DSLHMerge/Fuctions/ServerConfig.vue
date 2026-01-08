<template>
  <el-table :data="serverTable" style="width: 100%;" height="calc(100%)"
            size="small" table-layout="auto">
    <el-table-column prop="server_id" label="ID" show-overflow-tooltip align="center"/>
    <el-table-column prop="server_name" label="服务器名称" show-overflow-tooltip/>
<!--    <el-table-column prop="server_ip" label="服务器IP" show-overflow-tooltip/>-->
    <el-table-column prop="open_time" label="开服时间" show-overflow-tooltip/>
<!--    <el-table-column prop="database_user" label="数据库用户" show-overflow-tooltip/>-->
<!--    <el-table-column prop="database_name" label="数据库名称" show-overflow-tooltip/>-->
<!--    <el-table-column prop="database_port" label="数据库端口" show-overflow-tooltip align="center"/>-->
    <el-table-column prop="server_is_open" label="开启" show-overflow-tooltip align="center"/>
    <el-table-column prop="server_url" label="服务器URL" show-overflow-tooltip/>
    <el-table-column prop="server_port" label="服务器端口" show-overflow-tooltip align="center"/>
    <el-table-column prop="is_merged" label="合服" show-overflow-tooltip align="center"/>
    <el-table-column prop="server_type" label="服务器状态" show-overflow-tooltip align="center"/>
    <el-table-column label="编辑" align="center">
      <template #default="{row}">
        <el-button type="primary" size="small" @click="handleEdit(row)" plain circle>
          <el-icon>
            <EditPen/>
          </el-icon>
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script lang="ts" setup>
import {computed, defineEmits, defineProps} from 'vue';
import {DSLHGameAdminInfoStates} from "/@/views/dslhbackend/DSLHMerge/dslhgameadmininfo";
import {EditPen} from "@element-plus/icons-vue";

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

function handleReload() {
  emit('reload');
}

const props = defineProps<{ DSLHGameAdminInfo: DSLHGameAdminInfoStates }>()

const serverTable = computed(() => {
  const data = props.DSLHGameAdminInfo.data.server_config;
  const table = [];
  for (const key in data) {
    table.push(data[key]);
  }
  table.sort((a: any, b: any) => {
    return a.server_id - b.server_id;
  });
  return table;
})

function handleEdit(row: any) {
  console.log(row);
}

</script>