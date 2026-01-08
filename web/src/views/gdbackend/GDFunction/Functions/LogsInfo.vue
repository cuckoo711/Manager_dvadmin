<template>
  <el-divider content-position="left">
    <el-tag>必填信息</el-tag>
  </el-divider>
  <el-form :model="mustInfos" label-width="auto" label-position="left"
           :rules="mustInfosRules">

    <el-form-item label="日志种类">
      <el-select v-model="mustInfos.log_action" placeholder="请选择日志种类" filterable>
        <el-option v-for="item in props.GDGameBaseInfo.data.Actions" :key="item.label" :label="item.label"
                   :value="item.value"/>
      </el-select>
    </el-form-item>

    <el-form-item label="操作类型">
      <el-select v-model="mustInfos.log_reason" placeholder="请选择操作类型" filterable>
        <el-option v-for="item in props.GDGameBaseInfo.data.Reasons" :key="item.label" :label="item.label"
                   :value="item.value"/>
      </el-select>
    </el-form-item>
    <el-form-item label="区服选择">
      <el-select v-model="mustInfos.log_server" placeholder="请选择区服" filterable>
        <el-option v-for="item in props.GDGameBaseInfo.data.Servers" :key="item.label" :label="item.label"
                   :value="item.value"/>
      </el-select>
    </el-form-item>
  </el-form>

  <el-divider content-position="left">
    <el-tag>选填信息</el-tag>
  </el-divider>
  <el-form :model="mayInfos" :rules="mayInfosRules" label-width="auto" label-position="left">
    <el-form-item label="角色名称">
      <el-input v-model="mayInfos.log_pname" placeholder="请输入角色名称"/>
    </el-form-item>

    <el-form-item label="角色ID">
      <el-input v-model="mayInfos.log_pid" placeholder="请输入角色ID" @input="onRoleIdInput"/>
    </el-form-item>
  </el-form>
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="warning" @click="reSet">清空输入</el-button>
    <el-button type="success" @click="getLogs">导出日志</el-button>
  </el-button-group>
</template>

<script lang="ts" setup>
import {ref, watch} from 'vue';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";
import {GetLogs} from "/@/views/gdbackend/GDFunction/api";
import {ElMessage, ElMessageBox} from "element-plus";

const emit = defineEmits(['reload', 'logger']);

// function handleLogger(log: string, push: boolean = true) {
//   emit('logger', log, push);
// }
//
// function handleReload() {
//   emit('reload');
// }

const props = defineProps<{
  GDGameBaseInfo: GDGameBaseInfoStates;
}>()

const mustInfos = ref({
  log_action: '',
  log_reason: '',
  log_server: ''
})

const mustInfosRules = ref({
  log_action: [{required: true, message: '日志种类是必填项', trigger: 'change'}],
  log_reason: [{required: true, message: '操作类型是必填项', trigger: 'change'}],
  log_server: [{required: true, message: '区服选择是必填项', trigger: 'change'}],
});

const mayInfos = ref({
  log_pname: '',
  log_pid: ''
})

const mayInfosRules = ref({
  log_pid: [{pattern: /^[0-9]*$/, message: '角色ID只能是数字', trigger: 'blur'}]
})

function updateMustInfos() {
  if (props.GDGameBaseInfo.data.Actions.length > 0) {
    mustInfos.value.log_action = (
        props.GDGameBaseInfo.data.Actions.find((item) => item.label === '操作日志')?.value ||
        props.GDGameBaseInfo.data.Actions[0].value);
  }
  if (props.GDGameBaseInfo.data.Reasons.length > 0) {
    mustInfos.value.log_reason = props.GDGameBaseInfo.data.Reasons[0].value;
  }
  if (props.GDGameBaseInfo.data.Servers.length > 0) {
    mustInfos.value.log_server = props.GDGameBaseInfo.data.Servers[0].value;
  }
}

function reSet() {
  mustInfos.value = {
    log_action: '',
    log_reason: '',
    log_server: ''
  };
  mayInfos.value = {
    log_pname: '',
    log_pid: ''
  };
  updateMustInfos();
}

async function getLogs() {
  if (!props.GDGameBaseInfo.token) {
    ElMessage.error('请重载游戏信息');
    return;
  }
  if (!mustInfos.value.log_action || !mustInfos.value.log_reason || !mustInfos.value.log_server) {
    ElMessage.error('日志种类、操作类型、区服选择是必填项');
    return;
  }
  // 二次确认是否导出
  await ElMessageBox.confirm(
      '如过滤条件较少，导出日志可能会花费较长时间，是否继续?',
      '提示',
      {
        type: 'warning',
        confirmButtonText: '继续',
        cancelButtonText: '取消'
      }
  ).then(async () => {
    await GetLogs(
        props.GDGameBaseInfo.token,
        mustInfos.value.log_action,
        mustInfos.value.log_reason,
        mustInfos.value.log_server,
        mayInfos.value.log_pname,
        mayInfos.value.log_pid
    ).then((res) => {
      ElMessage.success(res.msg);
    })
  }).catch(() => {
    ElMessage.info('已取消');
  })
}

watch(() => props.GDGameBaseInfo.data, updateMustInfos, {deep: true});

function onRoleIdInput(value: string) {
  mayInfos.value.log_pid = value.replace(/[^0-9]/g, '');
}

</script>
