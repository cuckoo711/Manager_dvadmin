<template>
  <el-divider content-position="left">
    <el-tag>合服配置</el-tag>
  </el-divider>
  <el-form :model="form" :rules="formRules" label-width="auto" label-position="left">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="起始serverId" prop="startserverid">
          <el-input v-model="form.startserverid" placeholder="请输入起始serverId"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="结束serverId" prop="endserverid">
          <el-input v-model="form.endserverid" placeholder="请输入结束serverId"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="游戏数据库ip" prop="sqlip">
          <el-input v-model="form.sqlip" placeholder="请输入游戏数据库ip"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="游戏ip" prop="gameip">
          <el-input v-model="form.gameip" placeholder="请输入游戏ip"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="游戏端口" prop="gameport">
          <el-input v-model="form.gameport" placeholder="请输入游戏端口"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="是否合服" prop="ismerge">
          <el-radio-group v-model="form.ismerge">
            <el-radio-button label="0">否</el-radio-button>
            <el-radio-button label="1">是</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="状态" prop="state">
          <el-radio-group v-model="form.state">
            <el-radio-button label="1">新服</el-radio-button>
            <el-radio-button label="2">火爆</el-radio-button>
            <el-radio-button label="3">维护</el-radio-button>
            <el-radio-button label="4">屏蔽</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="是否显示" prop="isshow">
          <el-tooltip content="如果选择否,提交后所覆盖的所有区服将不再显示在区服列表中,但仍可通过区服id访问" placement="top">
            <el-radio-group v-model="form.isshow">
              <el-radio-button label="0">否</el-radio-button>
              <el-radio-button label="1">是</el-radio-button>
            </el-radio-group>
          </el-tooltip>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="warning" @click="Clear">清空</el-button>
    <el-button type="success" @click="Upload">提交</el-button>
  </el-button-group>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, ref, watch } from 'vue';
import { DSLHGameAdminInfoStates } from "/@/views/dslhbackend/DSLHMerge/dslhgameadmininfo";
import { ElMessage, ElMessageBox } from "element-plus";
import { GetGameServerMergeOpt } from "/@/views/dslhbackend/DSLHMerge/api";

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

function handleReload() {
  emit('reload');
}

const props = defineProps<{ DSLHGameAdminInfo: DSLHGameAdminInfoStates }>();

async function Upload() {
  if (form.value.startserverid > form.value.endserverid) {
    ElMessage.warning("起始serverId不能大于结束serverId");
    return;
  }
  if (form.value.sqlip === "") {
    ElMessage.warning("游戏数据库ip不能为空");
    return;
  }
  if (form.value.gameip === "") {
    ElMessage.warning("游戏ip不能为空");
    return;
  }
  if (form.value.gameport === "") {
    ElMessage.warning("游戏端口不能为空");
    return;
  }
  if (form.value.ismerge === "") {
    ElMessage.warning("是否合服不能为空");
    return;
  }
  if (form.value.state === "") {
    ElMessage.warning("状态不能为空");
    return;
  }
  if (form.value.isshow === "") {
    ElMessage.warning("是否显示不能为空");
    return;
  }
  await ElMessageBox.confirm('确定提交合服配置?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await GetGameServerMergeOpt(props.DSLHGameAdminInfo.data.server_id, form.value).then((res) => {
      if (res.status === 2000) {
        ElMessage.success(`已提交: ${res.message}`);
      } else {
        ElMessage.warning(`提交失败: ${res.message}`);
      }
      handleLogger(`提交合服配置: [${res.message}], 参数: ${JSON.stringify(form.value)}`);
    }).catch((err) => {
      ElMessage.warning(`提交失败: ${err}`);
      handleLogger(`提交合服配置: [${err}], 参数: ${JSON.stringify(form.value)}`);
    });
    handleReload();
  }).catch(() => {
    ElMessage.info('已取消提交');
  });
}

function Clear() {
  form.value = {
    "startserverid": Number(props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_id) || 100,
    "endserverid": Number(props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_id) || 100,
    "sqlip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_ip || "",
    "isshow": BOOL_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.server_is_open] || "0",
    "gameip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_url || "",
    "gameport": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_port || "",
    "ismerge": BOOL_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.is_merged] || "0", // (0：否，1：是)
    "state": SERVER_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.server_type] || "4", // (1：新服，2：火爆，3：维护，4：屏蔽)
  };
}

const form = ref<{
  "startserverid": number,
  "endserverid": number,
  "sqlip": string,
  "isshow": string,
  "gameip": string,
  "gameport": string,
  "ismerge": string,
  "state": string,
}>({
  "startserverid": 100,
  "endserverid": 100,
  "sqlip": "",
  "isshow": "0",
  "gameip": "",
  "gameport": "",
  "ismerge": "1", // (0：否，1：是)
  "state": "4", // (1：新服，2：火爆，3：维护，4：屏蔽)
});

const formRules = {
  startserverid: [{ required: true, message: '起始serverId不能为空', trigger: 'blur' }],
  endserverid: [{ required: true, message: '结束serverId不能为空', trigger: 'blur' }],
  sqlip: [{ required: true, message: '游戏数据库ip不能为空', trigger: 'blur' }],
  gameip: [{ required: true, message: '游戏ip不能为空', trigger: 'blur' }],
  gameport: [{ required: true, message: '游戏端口不能为空', trigger: 'blur' }],
  ismerge: [{ required: true, message: '是否合服不能为空', trigger: 'change' }],
  state: [{ required: true, message: '状态不能为空', trigger: 'change' }],
  isshow: [{ required: true, message: '是否显示不能为空', trigger: 'change' }],
};

const BOOL_STATE = {
  "是": "1",
  "否": "0",
};

const SERVER_STATE = {
  "新服": "1",
  "火爆": "2",
  "维护": "3",
  "屏蔽": "4",
};

watch(() => props.DSLHGameAdminInfo, (value: any) => {
  if (value.data.server_id) {
    form.value = {
      "startserverid": Number(props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_id) || 100,
      "endserverid": Number(props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_id) || 100,
      "sqlip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_ip || "",
      "isshow": BOOL_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.server_is_open] || "0",
      "gameip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_url || "",
      "gameport": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_port || "",
      "ismerge": BOOL_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.is_merged] || "0", // (0：否，1：是)
      "state": SERVER_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers?.[0]]?.server_type] || "4", // (1：新服，2：火爆，3：维护，4：屏蔾)
    }
  }
}, { immediate: true });
</script>
