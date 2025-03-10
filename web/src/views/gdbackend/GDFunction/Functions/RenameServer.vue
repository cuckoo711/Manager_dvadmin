<template>
  <el-form :model="editServer" label-width="auto" label-position="left">
    <el-divider content-position="left">
      <el-tag>区服冠名</el-tag>
    </el-divider>
    <el-form-item label="区服名称">
      <el-select v-model="editServer.serverId" placeholder="请选择区服" filterable @change="handleSelectServer">
        <el-option v-for="item in props.GDGameBaseInfo.data.Servers"
                   :key="item.label"
                   :label="item.label"
                   :value="item.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item v-if="combinedServers.length" label="已合区服">
      <el-select v-model="editServer.combinedServer" placeholder="请选择已合区服" filterable
                 @change="handleSelectCombinedServer">
        <el-option v-for="(item, index) in combinedServers"
                   :key="index"
                   :label="item.label"
                   :value="item.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="冠名名称">
      <el-input v-model="editServer.serverName" placeholder="请输入区服名称" clearable></el-input>
    </el-form-item>
  </el-form>
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="warning" @click="handleReSet">清空输入</el-button>
    <el-button type="success" @click="handleRenameServer">提交冠名</el-button>
  </el-button-group>
</template>

<script lang="ts" setup>
import {ref, watch} from "vue";
import {ElMessage} from "element-plus";
import {EditServerName} from "/@/views/gdbackend/GDFunction/api";
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";

const emit = defineEmits(["reload", "logger"]);

function handleLogger(log: string, push: boolean = true) {
  emit("logger", log, push);
}

function handleReload() {
  emit("reload");
  handleSelectServer();
}

const props = defineProps<{
  GDGameBaseInfo: GDGameBaseInfoStates
}>();

const editServer = ref({
  serverId: "",
  serverName: "",
  combinedServer: ""
});

const combinedServers = ref<Array<{ label: string; value: string; sortKey: number }>>([]);

function handleReSet() {
  Object.assign(editServer.value, {
    serverId: "",
    serverName: "",
    combinedServer: ""
  });
  combinedServers.value = [];
}

function handleSelectServer() {
  editServer.value.serverName = "";
  editServer.value.combinedServer = "";
  combinedServers.value = [];
  const serverId = editServer.value.serverId;
  const serverName = props.GDGameBaseInfo.data.Servers.find(item => item.value === serverId)?.label;

  if (!serverName) {
    handleLogger(`未找到区服ID: ${serverId} 的区服名称`);
    ElMessage.error(`未找到区服ID: ${serverId} 的区服名称`);
    return;
  }

  MatchCombinedServers()

  if (!combinedServers.value.length) {
    AutoServerNewName()
  }
}

function handleSelectCombinedServer() {
  if (editServer.value.combinedServer === editServer.value.serverId) {
    AutoServerNewName()
  } else {
    editServer.value.serverName = "";
  }
}

function AutoServerNewName() {
  const serverId = editServer.value.serverId;
  const serverName = props.GDGameBaseInfo.data.Servers.find(item => item.value === serverId)?.label;
  if (!serverName) {
    return;
  }
  const index = serverName.indexOf(")");
  if (index !== -1) {
    editServer.value.serverName = serverName.slice(0, index + 1);
  }
}

function MatchCombinedServers() {
  // 查找已合区服
  const serverId = editServer.value.serverId;
  const combinedService = props.GDGameBaseInfo.data.CombinedServices.find(
      item => item.label === serverId && item.value
  );

  if (combinedService) {
    const items = combinedService.value.split(',');

    const formattedData = [];
    for (let i = 0; i < items.length; i += 3) {
      formattedData.push({
        value: items[i],      // 第一项为 value
        label: items[i + 1],  // 第二项为 label
        sortKey: +items[i + 2] // 第三项用于排序（转为数字类型）
      });
    }
    formattedData.sort((a, b) => a.sortKey - b.sortKey);
    combinedServers.value = formattedData

  } else {
    combinedServers.value = [];
  }
}

async function handleRenameServer() {
  const {serverId, serverName, combinedServer} = editServer.value;
  if (!serverId || !serverName) {
    ElMessage.warning("区服和冠名内容不能为空");
    return;
  }

  const server = props.GDGameBaseInfo.data.Servers.find(item => item.value === serverId);
  if (!server) {
    ElMessage.warning("未找到对应区服");
    return;
  }

  const oldServerName = server.label;
  if (oldServerName === serverName) {
    ElMessage.warning("区服名称未发生变化");
    return;
  }

  let payload;
  let newName = serverName;
  if (combinedServers.value.length) {
    const combinedServiceStr = combinedServers.value
        .map(item => `${item.value},${item.label},${item.sortKey || ''}`)
        .join(',');
    const oldCombinedService_name = combinedServers.value.find(item => item.value === combinedServer)?.label;

    if (!oldCombinedService_name) {
      ElMessage.warning("未找到对应合区服");
      return;
    }
    payload = combinedServiceStr.replace(oldCombinedService_name, serverName);
    if (serverId !== combinedServer) {
      newName = oldServerName;
    }
  } else {
    payload = "";
  }

  await EditServerName(props.GDGameBaseInfo.token, serverId, newName, payload).then(res => {
    if (res.data !== true) {
      handleLogger("冠名区服失败, 请检查权限后重试");
      ElMessage.error("冠名区服失败, 请检查权限后重试");
      return;
    }
    handleLogger(`修改游戏 [${props.GDGameBaseInfo.data.GameName}] 区服 [${serverId}] 原[${oldServerName}]->[${serverName}]`);
    ElMessage.success("修改区服名称成功");
    server.label = `${serverId})${serverName}`;
    handleReload();
  }).catch(err => {
    handleLogger(`修改游戏 [${props.GDGameBaseInfo.data.GameName}] 区服 [${serverId}] 原[${oldServerName}]->[${serverName}] 失败: ${err}`);
    ElMessage.error("修改区服名称失败, 请查看日志");
  });
}

// 如果props.GDGameBaseInfo.data.Servers变化了
watch(() => props.GDGameBaseInfo.data.Servers, () => {
  MatchCombinedServers();
})

</script>
