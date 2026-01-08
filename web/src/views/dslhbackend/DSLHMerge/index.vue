<template>
  <fs-page>
    <el-container style="height: 100%;">
      <el-container style="padding: 20px;">
        <!-- 游戏选择区域 -->
        <el-header style="border-bottom: 2px solid #ccc;">
          <el-col>
            <el-text style="padding-right: 10px;">游戏选择:</el-text>
            <el-select v-model="selectedGame" filterable placeholder="请选择一款游戏"
                       style="width: 240px; padding-right: 10px;" @change="selectedGameChange">
              <el-option v-for="game in games" :key="game.id" :value="game.gamename">
                {{ game.gamename }}
              </el-option>
            </el-select>
            <el-button @click="loadGame" type="primary">重载游戏列表</el-button>
            <el-button @click="selectedGameChange" type="primary">重载游戏信息</el-button>
            <el-button @click="toggleAside" style="float: right;" type="text" v-if="!isAsideVisible">
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
            <el-tab-pane label="服务器配置" name="ServerConfig" lazy  style="height: 100%">
              <ServerConfig :DSLHGameAdminInfo="DSLHGameAdminInfo" @reload="selectedGameChange" @logger="log"/>
            </el-tab-pane>
            <el-tab-pane label="后台操作" name="MergeFuction" lazy style="height: 100%">
              <MergeFuction :DSLHGameAdminInfo="DSLHGameAdminInfo" @reload="selectedGameChange" @logger="log"/>
            </el-tab-pane>
            <el-tab-pane label="SQL操作" name="MergeFuctionSQL" lazy style="height: 100%">
              <MergeFuctionSQL :DSLHGameAdminInfo="DSLHGameAdminInfo" @reload="selectedGameChange" @logger="log"/>
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
  overflow: auto
}
</style>

<script lang="ts" setup>
import * as api from './api';
import {GetGameServerAdminInfo, PushLog} from './api';
import {defineAsyncComponent, onMounted, ref} from 'vue';

import {ElMessage, TabsPaneContext} from 'element-plus'
import {MessageBox} from "@element-plus/icons-vue";
import {DSLHGameAdminInfoStates} from "/@/views/dslhbackend/DSLHMerge/dslhgameadmininfo";
import LogViewer from "/@/views/dslhbackend/DSLHMerge/LogViewer.vue";

const ServerConfig = defineAsyncComponent(() => import('/@/views/dslhbackend/DSLHMerge/Fuctions/ServerConfig.vue'));
const MergeFuction = defineAsyncComponent(() => import('/@/views/dslhbackend/DSLHMerge/Fuctions/MergeFuction.vue'));
const MergeFuctionSQL = defineAsyncComponent(() => import('/@/views/dslhbackend/DSLHMerge/Fuctions/MergeFuctionSQL.vue'));

const debug = false;
const games = ref<{ id: number, gamename: string }[]>([]);
const selectedGame = ref('');
const logs = ref<string[]>([]);
const activeName = ref('ServerConfig');
const DSLHGameAdminInfo = ref<DSLHGameAdminInfoStates>(<DSLHGameAdminInfoStates>{data: {}})

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

  // 格式化日期并去掉自动附加的千分符，确保格式一致
  return `[${new Intl.DateTimeFormat('zh-CN', options).format(date).replace(/\u200E/g, '').replace(',', ' ')}] `;
};

const log = async (msg: string, push = true) => {
  const log_message = logtime() + msg;
  logs.value.push(log_message);
  if (push && !debug) {
    // 将日志推送到后端
    await PushLog(log_message);
  }
};

const loadGame = async () => {
  await log('开始加载游戏...', false)
  const res = await api.GetGameServersList({limit: 1000});
  games.value = res.data;
  await log('游戏加载完成, 共加载' + games.value.length + '款游戏后台', false);
  if (games.value.length > 0 && !selectedGame.value) {
    selectedGame.value = games.value[0]?.gamename;
    await selectedGameChange();
  }
};

const selectedGameChange = async () => {
  await log('已载入游戏后台配置: ' + selectedGame.value, false);

  // 找到对应的游戏数据
  const selectedGameData = games.value.find((game) => game.gamename === selectedGame.value);

  if (selectedGameData) {
    DSLHGameAdminInfo.value = await GetGameServerAdminInfo(String(selectedGameData.id));
    console.log("DSLHGameAdminInfo", DSLHGameAdminInfo.value);
    if (DSLHGameAdminInfo.value.data.servers.length === 0) {
      ElMessage.error('获取游戏信息失败, 请检查后台账号配置情况');
    }
  } else {
    await log('未找到对应的游戏数据');
  }
};

onMounted(() => {
  loadGame();
})
</script>