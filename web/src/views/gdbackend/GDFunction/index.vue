<template>
  <fs-page>
    <el-container style="height: 100%;">
      <el-container style="padding: 20px;">
        <!-- 游戏选择区域 -->
        <el-header style="border-bottom: 2px solid #ccc;">
          <el-col>
            <el-text style="padding-right: 10px;">游戏选择:</el-text>
            <el-select
                v-model="selectedGame"
                filterable
                placeholder="请选择一款游戏"
                style="width: 240px; padding-right: 10px;"
                @change="selectedGameChange"
            >
              <el-option
                  v-for="game in games"
                  :key="game.id"
                  :value="game.gamename"
              >
                {{ game.gamename }}
              </el-option>
            </el-select>
            <el-button-group>
              <el-button @click="loadGame" type="primary">重载游戏列表</el-button>
              <el-button @click="selectedGameChange" type="primary">重载游戏信息</el-button>
              <el-button @click="openGameBackend" type="primary">打开游戏后台</el-button>
            </el-button-group>
            <el-tag style="margin-left: 10px;">
              {{ configExist }}
            </el-tag>
            <el-button
                @click="toggleAside"
                style="float: right;"
                type="text"
                v-if="!isAsideVisible"
            >
              {{ isAsideVisible ? '收起日志' : '展开日志' }}
            </el-button>
          </el-col>
        </el-header>
        <el-main>
          <el-tabs
              class="tabs"
              v-model="activeName"
              @tab-click="handleClick"
              :tab-position="'left'"
              type="border-card"
              style="height: 100%"
          >
            <el-tab-pane label="发放邮件" name="SendEmail" lazy>
              <SendEmail
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
            <el-tab-pane label="礼包管理" name="GiftsManage" lazy>
              <GiftsManage
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
            <el-tab-pane label="区服冠名" name="RenameServer" lazy>
              <RenameServer
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
            <el-tab-pane label="红颜编辑" name="EditWife" lazy>
              <EditWife
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
            <el-tab-pane label="日志信息" name="LogsInfo" lazy>
              <LogsInfo
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
            <el-tab-pane label="活动管理" name="Activity" lazy>
              <Activity
                  :GDGameBaseInfo="GDGameBaseInfo"
                  @reload="selectedGameChange"
                  @logger="log"
              />
            </el-tab-pane>
          </el-tabs>
        </el-main>
      </el-container>

      <el-aside :width="isAsideVisible ? '35%' : '0'" transition>
        <el-card v-if="isAsideVisible" style="height: 100%">
          <template #header>
            <el-button class="card-header" @click="toggleAside" type="text">
              <span style="color: #00a0e1;">
                <el-icon><MessageBox/></el-icon>
                操作日志(点击收起)
              </span>
            </el-button>
          </template>
          <LogViewer :logs="logs"/>
        </el-card>
      </el-aside>
    </el-container>
  </fs-page>
</template>

<style lang="scss">
.el-tabs__content {
  height: 100%;
  overflow: auto;
}

.el-card__body {
  height: calc(100% - 80px);
}
</style>

<script lang="ts" setup>
import * as api from './api';
import {GetGameServerInfo, PushLog} from './api';
import {defineAsyncComponent, onMounted, ref} from 'vue';
import {GDGameBaseInfoStates} from '/@/views/gdbackend/GDFunction/gdgamebaseinfo';
import {ElMessage, TabsPaneContext} from 'element-plus';
import {MessageBox} from '@element-plus/icons-vue';
import LogViewer from "/@/views/gdbackend/GDFunction/LogViewer.vue";
import {CheckConfigExist} from "/@/views/gdbackend/GDFunction/Functions/AddActivity/api";

const SendEmail = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/SendEmail.vue'));
const GiftsManage = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/GiftsManage.vue'));
const RenameServer = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/RenameServer.vue'));
const EditWife = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/EditWife.vue'));
const LogsInfo = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/LogsInfo.vue'));
const Activity = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/Activity.vue'));

const debug = false;  // 如果为 true，log 不会推送到后端
const games = ref<{ id: number; gamename: string }[]>([]);
const selectedGame = ref('');
const logs = ref<string[]>([]);
const activeName = ref('SendEmail');
const GDGameBaseInfo = ref<GDGameBaseInfoStates>({
  data: {},
  token: '',
});
const configExist = ref<string>('');
const isAsideVisible = ref(true);
const toggleAside = () => {
  isAsideVisible.value = !isAsideVisible.value;
};

const handleClick = (tab: TabsPaneContext) => {
  console.log(tab.props.name);
};

const logtime: () => string = () => {
  const date = new Date();
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23', // 24小时制
    timeZone: 'Asia/Shanghai',
  };
  return `[${new Intl.DateTimeFormat('zh-CN', options)
      .format(date)
      .replace(/\u200E/g, '')
      .replace(',', ' ')}] `;
};

const log = async (msg: string, push = true) => {
  const log_message = logtime() + msg;
  logs.value.push(log_message);
  if (push && !debug) {
    // 将日志推送到后端
    await PushLog(log_message);
  }
};

const openGameBackend = async () => {
  if (GDGameBaseInfo.value.data.WebUrl) {
    window.open(GDGameBaseInfo.value.data.WebUrl);
  } else {
    ElMessage.error('未找到游戏后台地址');
  }
};

const loadGame = async () => {
  await log('开始加载游戏...', false);
  const res = await api.GetGameServersList({limit: 1000});
  games.value = res.data;
  await log('游戏加载完成, 共加载' + games.value.length + '款游戏后台', false);

  if (games.value.length > 0 && !selectedGame.value) {
    selectedGame.value = games.value[0]?.gamename;
    await selectedGameChange();
  }
};

const selectedGameChange = async () => {
  await log('已载入游戏配置: ' + selectedGame.value, false);

  // 找到对应的游戏数据
  const selectedGameData = games.value.find(
      (game) => game.gamename === selectedGame.value
  );

  if (selectedGameData) {
    GDGameBaseInfo.value = await GetGameServerInfo(String(selectedGameData.id));
    if (GDGameBaseInfo.value.data.Servers.length === 0) {
      ElMessage.error('获取游戏信息失败, 请检查后台账号配置情况');
    }
    await CheckConfigExist(GDGameBaseInfo.value.token).then((res) => {
      if (res.exist) {
        configExist.value = '活动配置存在';
      } else {
        configExist.value = '活动配置不存在';
      }
    });
  } else {
    await log('未找到对应的游戏数据');
  }
};

onMounted(() => {
  loadGame();
});
</script>
