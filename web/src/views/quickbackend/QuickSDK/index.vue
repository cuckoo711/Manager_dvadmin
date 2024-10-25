<!--suppress JSUnresolvedReference -->
<template>
  <fs-page>
    <div>
      <!-- 顶部：当前登录账户、游戏选择下拉框、按钮 -->
      <el-container>
        <el-card shadow="always" style="width: 100%;">
          <el-collapse v-model="isCollapsed">
            <el-collapse-item name="1" title="游戏选择">
              <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <el-tag style="font-size: 16px; margin-right: auto;">当前登录账户：{{ accountName }}</el-tag>
              </div>
              <el-table :data="[{}]" style="width: 100%">
                <el-table-column
                    label="游戏选择"
                    align="center"
                    header-align="center"
                >
                  <template #default="scope">
                    <el-select
                        v-model="selectedGame"
                        filterable
                        placeholder="请选择游戏"
                        clearable
                        @change="refreshChannelList"
                    >
                      <el-option
                          v-for="game in games"
                          :key="game.productId"
                          :label="game.gameName"
                          :value="game.productId"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column
                    label="操作"
                    align="center"
                    header-align="center"
                >
                  <template #default="scope">
                    <el-col>
                      <el-button type="primary" @click="reloadGameList">重新加载游戏列表</el-button>
                      <el-button type="primary" @click="refreshChannelList">刷新渠道状态</el-button>
                    </el-col>
                  </template>

                </el-table-column>
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-container>
    </div>
    <div :style="{height: 'calc(100% - 95px)'}">

      <!-- 渠道状态表格 -->
      <el-table
          :data="channelList"
          class="channel-table"
          style="width: 100%;"
          height="100%"
      >
        <el-table-column prop="channelId" label="渠道ID"></el-table-column>
        <el-table-column prop="channelName" label="渠道名"></el-table-column>
        <el-table-column prop="noLogin" label="登录">
          <template #default="scope">
            <el-icon v-if="scope.row.noLogin">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="noPay" label="支付">
          <template #default="scope">
            <el-icon v-if="scope.row.noPay">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="noRegister" label="注册">
          <template #default="scope">
            <el-icon v-if="scope.row.noRegister">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <!-- 开/关登录、支付、注册 -->
            <el-button type="primary" size="small"
                       @click="handleSwitch(scope.row.channelId, 'noLogin', !scope.row.noLogin)">
              {{ scope.row.noLogin ? '关闭' : '开启' }}登录
            </el-button>
            <el-button type="primary" size="small"
                       @click="handleSwitch(scope.row.channelId, 'noPay', !scope.row.noPay)">
              {{ scope.row.noPay ? '关闭' : '开启' }}支付
            </el-button>
            <el-button type="primary" size="small"
                       @click="handleSwitch(scope.row.channelId, 'noRegister', !scope.row.noRegister)">
              {{ scope.row.noRegister ? '关闭' : '开启' }}注册
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </fs-page>
</template>

<script>
import {GetGameList, GetUser, SwitchGame} from "/@/views/quickbackend/QuickSDK/api";
import {ElMessage} from "element-plus";
import {CircleCheckFilled, CircleCloseFilled} from "@element-plus/icons-vue";
import {ref} from 'vue'

export default {
  name: 'QuickSDK',
  components: {CircleCloseFilled, CircleCheckFilled},
  data() {
    return {
      accountName: '',
      selectedGame: ref(''),
      games: [],
      channelList: [],
    };
  },
  mounted() {
    this.fetchAccountInfo();
    this.reloadGameList();
    window.addEventListener('resize', this.updateTableHeight);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateTableHeight);
  },
  methods: {
    async fetchAccountInfo() {
      const response = await GetUser();
      if (response.status) {
        this.accountName = response.username;
      } else {
        ElMessage.error(response.message);
      }
    },
    async reloadGameList() {
      const response = await GetGameList();
      if (response.status) {
        this.games = response.data;
        console.log(this.games);
      } else {
        ElMessage.error(response.message);
      }
    },
    async refreshChannelList() {
      if (!this.selectedGame) return;
      const response = await SwitchGame(this.selectedGame);
      if (!response.status) {
        ElMessage.error(response.message);
        return;
      }
      this.channelList = Object.entries(response.data).map(([channelId, channelData]) => ({
        channelId,
        channelName: channelData.channel_name,
        noLogin: channelData.no_login,
        noPay: channelData.no_pay,
        noRegister: channelData.no_register
      }));
    },
    async handleSwitch(channelId, type, value) {
      console.log(channelId, type, value);
    }
  },
}
</script>