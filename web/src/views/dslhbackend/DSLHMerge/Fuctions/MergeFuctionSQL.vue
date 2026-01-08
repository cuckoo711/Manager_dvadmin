<!--suppress CssUnusedSymbol -->
<template>
  <el-divider content-position="left">
    <el-tag>数据库配置</el-tag>
  </el-divider>
  <el-form :model="form" :rules="formRules" ref="formRef" label-width="auto" label-position="left">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="服务器IP" prop="remote_ip">
          <el-input v-model="form.remote_ip" placeholder="请输入服务器IP"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="服务器密码" prop="remote_password">
          <el-tooltip content="请注意,此处若留空,则使用默认密码" placement="top">
            <el-input v-model="form.remote_password" placeholder="若留空,则使用默认密码" show-password></el-input>
          </el-tooltip>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="数据库密码" prop="mysql_password">
          <el-input v-model="form.mysql_password" placeholder="请输入数据库密码" show-password></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="数据库前缀" prop="prefix">
          <el-input v-model="form.prefix" placeholder="请输入数据库前缀"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="待操作区服">
          <el-input v-model="form.merge_ids" disabled placeholder="选择区服后自动填充"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="曾合过区服">
          <el-input v-model="form.merged_ids" disabled placeholder="选择区服后自动填充"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
  <el-form :model="form" :rules="formRules" label-width="auto" label-position="left">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="起始ID" prop="start_id">
          <el-input v-model="form.start_id" placeholder="请输入起始ID"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="结束ID" prop="end_id">
          <el-input v-model="form.end_id" placeholder="请输入结束ID"></el-input>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="目标ID" prop="dest_id">
          <el-input v-model="form.dest_id" placeholder="请输入目标ID"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
  <div class="edit_dev">
    <el-transfer
        v-if="showTransfer"
        ref="serverTransferRef"
        v-model="selectionServers" :data="transferData"
        :titles="['可操作区服', '待操作区服']"
    >
      <template #left-empty>
        <el-empty :image-size="60" description="暂无可操作区服"/>
      </template>
      <template #right-empty>
        <el-empty :image-size="60" description="暂无待操作区服"/>
      </template>
    </el-transfer>
  </div>
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="warning" @click="Clear">清空</el-button>
    <el-button type="success" @click="Upload">提交</el-button>
  </el-button-group>

</template>
<script setup lang="ts">
import {defineEmits, defineProps, nextTick, ref, watch} from 'vue';
import {DSLHGameAdminInfoStates} from "/@/views/dslhbackend/DSLHMerge/dslhgameadmininfo";
import {Option} from "element-plus/es/components/segmented/src/types";
import {ElMessage, ElMessageBox, ElTransfer} from "element-plus";
import {GetGameServerMergeSql} from "/@/views/dslhbackend/DSLHMerge/api";

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

function handleReload() {
  emit('reload');
}

const props = defineProps<{ DSLHGameAdminInfo: DSLHGameAdminInfoStates }>()

const selectionServers = ref<string[]>([])
const serverTransferRef = ref<any>()
const showTransfer = ref(true);

// 清除 serverTransfer 的勾选状态方法
function clearSelection() {
  showTransfer.value = false;
  nextTick(() => {
    showTransfer.value = true;
  });
}

const formRules = {
  remote_ip: [{required: true, message: '请输入服务器IP', trigger: 'blur'}],
  remote_password: [{message: '请输入服务器密码', trigger: 'blur'}],
  mysql_password: [{required: true, message: '请输入数据库密码', trigger: 'blur'}],
  prefix: [{required: true, message: '请输入数据库前缀', trigger: 'blur'}],
  start_id: [{required: true, message: '请输入起始ID', trigger: 'blur'}],
  end_id: [{required: true, message: '请输入结束ID', trigger: 'blur'}],
  dest_id: [{required: true, message: '请输入目标ID', trigger: 'blur'}],
};

async function Upload() {
  if (form.value.remote_ip === "") {
    ElMessage.warning("服务器IP不能为空");
    return;
  }
  if (form.value.prefix === "") {
    ElMessage.warning("数据库前缀不能为空");
    return;
  }
  if (form.value.mysql_password === "") {
    ElMessage.warning("数据库密码不能为空");
    return;
  }
  if (form.value.start_id === "") {
    ElMessage.warning("起始ID不能为空");
    return;
  }
  if (form.value.end_id === "") {
    ElMessage.warning("结束ID不能为空");
    return;
  }
  if (form.value.dest_id === "") {
    ElMessage.warning("目标ID不能为空");
    return;
  }
  if (form.value.merge_ids.length === 0 && form.value.merged_ids.length === 0) {
    ElMessage.warning("待操作区服和曾合过区服不能同时为空");
    return;
  }
  await ElMessageBox.confirm('确定提交合服配置?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await GetGameServerMergeSql(form.value).then((res: any) => {
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

const form = ref<{
  remote_ip: string;
  remote_password: string;
  mysql_password: string;
  prefix: string;
  start_id: string;
  end_id: string;
  dest_id: string;
  merge_ids: string[];
  merged_ids: string[];
}>({
  remote_ip: "",
  remote_password: "0",
  mysql_password: "",
  prefix: "",
  start_id: "",
  end_id: "",
  dest_id: "",
  merge_ids: [],
  merged_ids: [],
});

function Clear() {
  form.value = {
    "remote_ip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_ip || "",
    "remote_password": "",
    "mysql_password": "",
    "prefix": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].database_name.replace(/\d+$/, '') || "",
    "start_id": "",
    "end_id": "",
    "dest_id": "",
    "merge_ids": [],
    "merged_ids": [],
  }
  transferData.value = generateData()
  clearSelection()
}


const BOOL_STATE = {
  "是": "1",
  "否": "0",
};

function checkDisabled(i: number) {
  return props.DSLHGameAdminInfo.data.no_recharges.includes(props.DSLHGameAdminInfo.data.servers[i]) ||
      BOOL_STATE[props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].server_is_open] == "0" ||
      props.DSLHGameAdminInfo.data.servers[i] == "测试服"
}

function getServerName(i: number) {
  const server_name = props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].server_name
  let addStr = '(' + props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].server_id + ')'
  if (props.DSLHGameAdminInfo.data.no_recharges.includes(server_name)) {
    addStr += " (无充值)"
  }
  if (props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].is_merged == "是") {
    addStr += " (已合服)"
  }
  return server_name + addStr
}

function is_merged(id: string) {
  return Object.values(props.DSLHGameAdminInfo.data.server_config || {}).find((server: any) => server.server_id === id)?.is_merged == "是" || false
}

const generateData = () => {
  const data: Option[] = []
  for (let i = 0; i < props.DSLHGameAdminInfo.data.servers?.length || 0; i++) {
    data.push({
      key: props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].server_id,
      label: getServerName(i),
      value: props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[i]].server_id,
      disabled: checkDisabled(i)
    })
  }
  return data;
}
const transferData = ref<any>(generateData())
watch(
    () => props.DSLHGameAdminInfo, (value: any) => {
      transferData.value = []
      if (value.data.server_id) {
        form.value = {
          "remote_ip": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].server_ip || "",
          "remote_password": "",
          "mysql_password": "",
          "prefix": props.DSLHGameAdminInfo.data.server_config?.[props.DSLHGameAdminInfo.data.servers[0]].database_name.replace(/\d+$/, '') || "",
          "start_id": "",
          "end_id": "",
          "dest_id": "",
          "merge_ids": [],
          "merged_ids": [],
        }
        transferData.value = generateData()
      }
      selectionServers.value = []
      nextTick(() => {
        clearSelection()
      })
    },
    {immediate: true}
)

watch(
    () => form.value.start_id,
    (value: string) => {
      if (value) {
        form.value.dest_id = String(100 + Number(value));
      }
    },
    {immediate: true}
);

watch(
    () => form.value.end_id,
    (value: string) => {
      if (value) {
        // 从起始ID和结束ID中获取区服ID列表，包含起始和结束ID
        const start = Number(form.value.start_id);
        const end = Number(value);
        // 如果起始ID大于结束ID，则交换两者的值
        if (start > end) {
          form.value.start_id = value;
          form.value.end_id = String(start);
        }
        // 如果起始ID不存在于transferData中
        if (!transferData.value.find((item: any) => item.value == String(Number(form.value.start_id) + 100))) {
          ElMessage.warning("起始ID不存在于可操作区服中");
          selectionServers.value = []
          return
        }
        // 如果结束ID不存在于transferData中
        if (!transferData.value.find((item: any) => item.value == String(Number(form.value.end_id) + 100))) {
          ElMessage.warning("结束ID不存在于可操作区服中");
          selectionServers.value = []
          return
        }
        // 如果起始ID和结束ID都存在，则生成区服ID列表
        if (form.value.start_id && form.value.end_id) {
          const ids = [];
          for (let i = start; i <= end; i++) {
            ids.push(String(i + 100));
          }
          // 从transferData中获取区服ID列表且disabled为false的区服ID
          const server_ids = transferData.value.filter((item: any) => !item.disabled).map((item: any) => item.value);
          // 从ids中过滤出transferData中存在的区服ID
          selectionServers.value = ids.filter((id) => server_ids.includes(id))
        } else {
          selectionServers.value = []
        }
      } else {
        selectionServers.value = []
      }
    },
    {immediate: true}
);

watch(
    () => selectionServers.value,
    (value: string[]) => {
      // 把每个区服ID过一遍is_merged函数，将已合服的区服ID放到merged_ids中，未合服的区服ID放到merge_ids中
      form.value.merged_ids = value.filter(is_merged)
      form.value.merge_ids = value.filter((id) => !is_merged(id))
      // 将merge_ids按从大到小排序，将merged_ids按从小到大排序
      form.value.merge_ids.sort((a, b) => Number(b) - Number(a))
      form.value.merged_ids.sort((a, b) => Number(a) - Number(b))
      // 转为数组
      form.value.merge_ids = form.value.merge_ids.map((id) => String(Number(id) - 100))
      form.value.merged_ids = form.value.merged_ids.map((id) => String(Number(id) - 100))
    },
    {immediate: true}
);

</script>
<style scoped>
.edit_dev >>> .el-transfer-panel {
  width: calc(50% - 100px);
}
</style>