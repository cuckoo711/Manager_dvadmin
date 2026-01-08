<template>
  <el-divider content-position="left">
    <el-tag>配置活动</el-tag>
  </el-divider>
  <el-form :model="form" label-width="auto" label-position="left">
    <el-form-item label="区服选择">
      <el-select
        v-model="form.server"
        placeholder="请选择区服"
        filterable
        style="width: calc(100% - 145px) !important; margin-right: 20px"
      >
        <el-option
          v-for="item in props.GDGameBaseInfo.data.Servers"
          :key="item.label"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button :icon="CirclePlus" @click="addServer" type="text">
        添加
      </el-button>
    </el-form-item>

    <!-- 上传区服 -->
    <el-form-item label="上传区服">
      <el-input
        type="textarea"
        v-model="form.upload"
        placeholder="请添加区服"
        :autosize="{ minRows: 2, maxRows: 4 }"
        disabled
        style="width: calc(100% - 145px) !important; margin-right: 20px"
      />
      <el-tooltip content="自动添加" placement="top">
        <el-button :icon="MagicStick" @click="MatchAdd" type="text">
          匹配
        </el-button>
      </el-tooltip>
      <el-tooltip content="清空" placement="top">
        <el-button :icon="RefreshRight" @click="Clear" type="text">
          清空
        </el-button>
      </el-tooltip>
    </el-form-item>

    <!-- 活动开始日期 -->
    <el-form-item label="活动开始日期">
      <el-date-picker
        v-model="form.startDate"
        type="date"
        placeholder="选择日期"
        :shortcuts="shortcuts"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
      />
    </el-form-item>

    <!-- 区服活动范围 -->
    <el-form-item label="区服活动跨度">
      <el-input-number :min="0" :max="8" v-model="form.rangeStart" />
    </el-form-item>

    <!-- 跨服活动范围 -->
    <el-form-item label="跨服活动跨度">
      <el-input-number :min="0" :max="8" v-model="form.rangeEnd" />
    </el-form-item>
  </el-form>

  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>

  <!--
    修改：将原本 @click="showAddActivityVisible = true" 改为
    @click="openAddActivityDrawer"
    这样在点按钮时会先复制游戏名，然后再打开抽屉
  -->
  <el-button-group>
    <el-button type="primary" @click="openAddActivityDrawer">上传活动配置</el-button>
    <el-button type="primary" @click="showEditActivityVisible = true">活动详情</el-button>
    <el-button type="success" @click="handleUpload">上传活动</el-button>
  </el-button-group>

  <el-drawer
    v-model="showAddActivityVisible"
    title="上传活动配置"
    size="80%"
    class="rounded-lg"
    destroy-on-close
  >
    <template #header>
      <div>
        上传活动配置:
        <el-tag style="margin-right: 20px"
          >{{ props.GDGameBaseInfo.data.GameName }}</el-tag
        >
      </div>
    </template>
    <AddActivity
      :GDGameBaseInfo="props.GDGameBaseInfo"
      @close="closeAddActivityDrawer"
      @reload="handleReload"
      @logger="handleLogger"
    />
  </el-drawer>

  <el-drawer
    v-model="showEditActivityVisible"
    title="当前活动详情"
    size="80%"
    class="rounded-lg"
    destroy-on-close
  >
    <template #header>
      <div>
        当前活动详情:
        <el-tag style="margin-right: 20px"
          >{{ props.GDGameBaseInfo.data.GameName }}</el-tag
        >
      </div>
    </template>
    <EditActivity
      :GDGameBaseInfo="props.GDGameBaseInfo"
      @reload="handleReload"
      @logger="handleLogger"
    />
  </el-drawer>

  <el-dialog
    v-model="logDialogVisible"
    :title="logTitle"
    width="30%"
    :destroy-on-close="true"
  >
    <el-tree
      :data="logData"
      node-key="label"
      default-expand-all
      :props="{ label: 'label', children: 'children' }"
    />
    <template #footer>
      <el-button @click="logDialogVisible = false" type="primary"
        >关闭</el-button
      >
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { defineAsyncComponent, ref } from 'vue';
import { GDGameBaseInfoStates } from '/@/views/gdbackend/GDFunction/gdgamebaseinfo';
import {
  GetLatestServers,
  UploadServerActivity,
} from '/@/views/gdbackend/GDFunction/api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CirclePlus, MagicStick, RefreshRight } from '@element-plus/icons-vue';

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

function handleReload() {
  emit('reload');
}


const props = defineProps<{ GDGameBaseInfo: GDGameBaseInfoStates }>();
const AddActivity = defineAsyncComponent(() =>
  import('/@/views/gdbackend/GDFunction/Functions/AddActivity/index.vue')
);
const EditActivity = defineAsyncComponent(() =>
  import('/@/views/gdbackend/GDFunction/Functions/EditActivity/index.vue')
);
const showAddActivityVisible = ref(false);
const showEditActivityVisible = ref(false);

const closeAddActivityDrawer = () => {
  showAddActivityVisible.value = false;
}
interface TreeNode {
  label: string;
  children?: TreeNode[];
}

const logDialogVisible = ref(false); // 控制弹窗显示
const logData = ref<TreeNode[]>([]); // 存储树形数据
const logTitle = ref(''); // 弹窗标题
const logType = ref('success'); // 弹窗类型（成功/失败）
function parseLog(log: Record<string, string[]>) {
  return Object.entries(log).map(([server, messages]) => ({
    label:
      props.GDGameBaseInfo.data.Servers.find((s) => s.value === server)?.label ||
      server,
    children: messages.map((message) => ({ label: message })),
  }));
}

const form = ref<{
  server: string;
  upload: string;
  rangeStart: number;
  rangeEnd: number;
  startDate: string;
}>({
  server: '',
  upload: '',
  rangeStart: 2,
  rangeEnd: 4,
  startDate: new Date(new Date().setDate(new Date().getDate() + 1))
    .toISOString()
    .split('T')[0],
});

const shortcuts = [
  {
    text: '明天',
    value: () => {
      const date = new Date();
      date.setTime(date.getTime() + 3600 * 1000 * 24); // 加一天
      return date;
    },
  },
  {
    text: '后两天',
    value: () => {
      const date = new Date();
      date.setTime(date.getTime() + 3600 * 1000 * 24 * 2); // 加两天
      return date;
    },
  },
  {
    text: '后三天', // 大后天
    value: () => {
      const date = new Date();
      date.setTime(date.getTime() + 3600 * 1000 * 24 * 3); // 加三天
      return date;
    },
  },
  {
    text: '后四天', // 大大后天
    value: () => {
      const date = new Date();
      date.setTime(date.getTime() + 3600 * 1000 * 24 * 4); // 加四天
      return date;
    },
  },
];

function addServer() {
  const selectedServer = form.value.server;

  // 检查是否选择了区服
  if (selectedServer) {
    const serverOption = props.GDGameBaseInfo.data.Servers.find(
      (server) => server.value === selectedServer
    );

    // 如果找到对应的区服
    if (serverOption) {
      const serverLabelValue = `${serverOption.value}(${serverOption.label})`; // 组合label和value
      // 如果upload已经有内容，添加逗号分隔
      if (form.value.upload) {
        form.value.upload += `, ${serverLabelValue}`;
      } else {
        form.value.upload = serverLabelValue;
      }
    }
  } else {
    // 如果没有选择区服，提示错误
    ElMessage.warning('请选择一个区服');
  }
}

function Clear() {
  // 清空上传区服的内容
  form.value.upload = '';
  // 清空区服选择
  form.value.server = '';
}

async function MatchAdd() {
  form.value.upload = '';
  await GetLatestServers(props.GDGameBaseInfo.token)
    .then((res) => {
      if (res.data) {
        if (res.data[1].length > 0) {
          for (let i = 0; i < res.data[1].length; i++) {
            const serverOption = props.GDGameBaseInfo.data.Servers.find(
              (server) => server.value === res.data[1][i]
            );
            if (serverOption) {
              const serverLabelValue = `${serverOption.value}(${serverOption.label})`; // 组合label和value
              // 如果upload已经有内容，添加逗号分隔
              if (form.value.upload) {
                form.value.upload += `, ${serverLabelValue}`;
              } else {
                form.value.upload = serverLabelValue;
              }
            }
          }
          form.value.startDate = res.data[0];
          form.value.rangeEnd = Number(res.data[2]);
        } else {
          ElMessage.warning('没有最新区服');
        }
      } else {
        ElMessage.error('获取最新区服失败');
      }
    })
    .catch((err) => {
      ElMessage.error('获取最新区服失败');
      handleLogger(`获取最新区服失败: ${err.toString()}`);
    });
}

async function handleUpload() {
  if (!form.value.upload) {
    ElMessage.warning('请添加区服');
    return;
  }
  if (!form.value.startDate) {
    ElMessage.warning('请选择活动开始日期');
    return;
  }
  if (!form.value.rangeStart) {
    ElMessage.warning('请选择区服活动跨度');
    return;
  }
  if (!form.value.rangeEnd) {
    ElMessage.warning('请选择跨服活动跨度');
    return;
  }
  // 将区服按逗号分隔, 并只保留区服ID
  const serverListString = form.value.upload
    .split(',')
    .map((server) => {
      return server.split('(')[0].trim();
    })
    .join(',');

  await ElMessageBox.confirm('确定上传活动配置?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await UploadServerActivity(
        props.GDGameBaseInfo.token,
        serverListString,
        String(form.value.rangeStart),
        String(form.value.rangeEnd),
        form.value.startDate
      )
        .then((res) => {
          if (res.data) {
            // 上传成功
            logType.value = 'success';
            logTitle.value = res.data.message || '上传成功';
            logData.value = parseLog(res.data.log);
          } else {
            // 上传失败
            logType.value = 'error';
            logTitle.value = res.data.message || '上传失败';
            logData.value = parseLog(res.data.log);
          }
          logDialogVisible.value = true; // 显示弹窗
        })
        .catch((err) => {
          ElMessage.error('上传失败');
          handleLogger(`上传失败: ${err.toString()}`);
        });
    })
    .catch(() => {
      // 取消上传
      ElMessage.info('已取消上传');
    });
}

/**
 * 新增：复制游戏名到剪贴板
 */
function copyGameName() {
  const gameName = props.GDGameBaseInfo.data.GameName;
  if (!gameName) {
    ElMessage.warning('游戏名为空，无法复制');
    return;
  }

  // 如果浏览器支持 clipboard API
  if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(gameName)
      .then(() => {
        ElMessage.success(`已复制游戏名：${gameName}`);
      })
      .catch(() => {
        ElMessage.error('复制游戏名失败');
      });
  } else {
    // 如果不支持，可考虑使用其它方案或弹窗提示
    ElMessage.error('当前浏览器不支持复制功能');
  }
}

/**
 * 新增：打开上传活动配置抽屉前，先复制游戏名到剪贴板
 */
function openAddActivityDrawer() {
  copyGameName();
  showAddActivityVisible.value = true;
}
</script>
