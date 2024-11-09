<template>
  <fs-page>
    <div>
      <!-- 顶部：当前登录账户、游戏选择下拉框、按钮 -->
      <el-container>
        <el-card shadow="always" style="width: 100%;">
          <el-collapse v-model="isCollapsed">
            <el-collapse-item name="1" :disabled="!accountNameValid">
              <template #title>
                <div>
                  当前登录账户：
                  <el-tag v-if="accountNameValid">
                    <a href="/#/Quick/account" target="_blank">{{ accountName }}</a>
                  </el-tag>
                  <el-tag v-else>{{ accountName }}</el-tag>
                </div>
              </template>
              <el-table :data="[{}]" style="width: 100%">
                <!-- 游戏选择下拉框 -->
                <el-table-column
                    label="游戏选择"
                    align="center"
                    header-align="center"
                    min-width="300"
                >
                  <template #default="scope">
                    <el-select
                        v-model="selectedGame"
                        :disabled="!accountNameValid"
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
                <!-- 渠道后缀筛选下拉框 -->
                <el-table-column
                    label="渠道后缀筛选"
                    align="center"
                    header-align="center"
                    min-width="200"
                >
                  <template #default="scope">
                    <el-select
                        v-model="channelSuffix"
                        :disabled="!accountNameValid"
                        filterable
                        placeholder="请选择渠道后缀"
                        clearable
                        @change="refreshChannelList"
                    >
                      <el-option
                          v-for="suffix in channelSuffixList"
                          :key="suffix"
                          :label="suffix"
                          :value="suffix"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                <!-- 批量操作下拉框 -->
                <el-table-column
                    label="批量操作"
                    align="center"
                    header-align="center"
                    min-width="300"
                >
                  <template #default="scope">
                    <el-row>
                      <el-col :span="16">
                        <el-select
                            v-model="batchSwitchType"
                            :disabled="!accountNameValid"
                            filterable
                            placeholder="请选择批量操作"
                        >
                          <el-option-group
                              v-for="group in batchSwitchList"
                              :key="group.label"
                              :label="group.label"
                          >
                          <el-option
                              v-for="item in group.options"
                              :key="item.value"
                              :label="item.type"
                              :value="item.value"
                          />
                          </el-option-group>
                        </el-select>
                      </el-col>
                      <el-col :span="8">
                        <el-button
                            type="primary"
                            :disabled="!accountNameValid"
                            @click="handleBatchSwitch"
                        >
                          执行
                        </el-button>
                      </el-col>
                    </el-row>
                  </template>
                </el-table-column>
                <!-- 操作按钮 -->
                <el-table-column
                    label="操作"
                    align="center"
                    header-align="center"
                    min-width="220"
                >
                  <template #default="scope">
                    <el-row>
                      <el-col :span="12">
                        <el-button
                            type="primary"
                            size="small"
                            :disabled="!accountNameValid"
                            @click="reloadGameList"
                        >
                          重载游戏列表
                        </el-button>
                      </el-col>
                      <el-col :span="12">
                        <el-button
                            type="primary"
                            size="small"
                            :disabled="!accountNameValid"
                            @click="refreshChannelList"
                        >
                          刷新渠道状态
                        </el-button>
                      </el-col>
                    </el-row>
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
          @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55"/>
        <el-table-column prop="channelId" label="渠道ID" sortable></el-table-column>
        <el-table-column prop="channelName" label="渠道名"></el-table-column>
        <el-table-column prop="noLogin" label="登录" sortable>
          <template #default="scope">
            <el-icon v-if="!scope.row.noLogin">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="noPay" label="支付" sortable>
          <template #default="scope">
            <el-icon v-if="!scope.row.noPay">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="noRegister" label="注册" sortable>
          <template #default="scope">
            <el-icon v-if="!scope.row.noRegister">
              <CircleCheckFilled style="color: green;"/>
            </el-icon>
            <el-icon v-else>
              <CircleCloseFilled style="color: red;"/>
            </el-icon>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </fs-page>
</template>

<script>
import {
  GetChannelSuffix,
  GetGameList,
  GetUser,
  SwitchGame,
  UpdateChannelStatus
} from "/@/views/quickbackend/QuickSDK/api";
import {ElMessage} from "element-plus";
import {CircleCheckFilled, CircleCloseFilled} from "@element-plus/icons-vue";
import {ref} from 'vue'

export default {
  name: 'QuickSDK',
  components: {CircleCloseFilled, CircleCheckFilled},
  data() {
    return {
      isCollapsed: [],
      accountName: '',
      selectedGame: ref(''),
      channelSuffix: ref('全部'),
      games: [],
      channelList: [],
      channelSuffixList: ['全部', '无后缀'],
      multipleSelection: ref({}),
      batchSwitchType: ref(''),
      batchSwitchList: [
        {
          label: '-----批量关-----',
          options: [
            {type: '批量关注册', value: '0'},
            {type: '批量关支付', value: '1'},
            {type: '批量关登录', value: '2'}]
        },
        {
          label: '-----批量开-----',
          options: [
            {type: '批量开注册', value: '3'},
            {type: '批量开支付', value: '4'},
            {type: '批量开登录', value: '5'}
          ]
        }
      ]
    }
  },
  computed: {
    // 计算属性，用于判断是否有有效的账户信息
    accountNameValid() {
      return this.accountName && this.accountName !== '请先在Quick操作账号中添加账号';
    }
  },
  mounted() {
    this.fetchAccountInfo();
    this.reloadGameList();
    this.loadChannelSuffixList();
  },
  methods: {
    async fetchAccountInfo() {
      const response = await GetUser();
      if (response.status) {
        this.accountName = response.username;
      } else {
        this.accountName = '请先在Quick操作账号中添加账号';
        ElMessage.error(response.message);
      }
    },
    async reloadGameList() {
      const response = await GetGameList();
      if (response.status) {
        this.games = response.data;
        ElMessage.success('游戏列表已重新加载');
      } else {
        ElMessage.error(response.message);
      }
    },
    async refreshChannelList() {
      if (!this.selectedGame) return;
      const response = await SwitchGame(this.selectedGame, this.channelSuffix);
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
      ElMessage.success('渠道状态列表已刷新');
    },
    async loadChannelSuffixList() {
      const response = await GetChannelSuffix();
      if (!response.status) {
        ElMessage.error(response.message);
        return;
      }
      this.channelSuffixList = ['全部', '无后缀', ...response.data];
      ElMessage.success('渠道后缀列表已刷新');
    },
    async handleBatchSwitch() {
      if (!this.selectedGame) {
        ElMessage.error('请选择游戏');
        return;
      }
      if (!this.batchSwitchType) {
        ElMessage.error('请选择批量操作类型');
        return;
      }
      if (Object.keys(this.multipleSelection).length === 0) {
        const confirmedAllChannels = await this.confirmAllChannels();
        if (!confirmedAllChannels) {
          return;
        }
      }
      if (Object.keys(this.multipleSelection).length > 0) {
        const confirmedBatch = await this.confirmBatchOperation();
        if (confirmedBatch) {
          await this.handleBatchSwitchConfirm();
        }
      } else {
        ElMessage.info('没有渠道可供操作');
      }
    },
    async confirmAllChannels() {
      try {
        await this.$confirm('未选择任何渠道，是否对所有渠道执行此操作？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        this.multipleSelection = this.channelList.reduce((acc, channel) => {
          acc[channel.channelId] = {
            channel_name: channel.channelName,
            no_login: channel.noLogin,
            no_pay: channel.noPay,
            no_register: channel.noRegister
          };
          return acc;
        }, {});

        return true;
      } catch {
        ElMessage.info('已取消操作');
        return false;
      }
    },
    async confirmBatchOperation() {
      try {
        await this.$confirm(`确定要对这${Object.keys(this.multipleSelection).length}条记录执行批量操作吗`, '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          closeOnClickModal: false,
        });
        return true;
      } catch {
        ElMessage.info('已取消操作');
        return false;
      }
    },
    async handleBatchSwitchConfirm() {
      const response = await UpdateChannelStatus(
          this.selectedGame,
          this.batchSwitchType,
          this.multipleSelection
      );
      if (!response.status) {
        ElMessage.error(response.message);
        return;
      }
      ElMessage.success('批量操作成功');
      await this.refreshChannelList();
      this.multipleSelection = {};
    }

  },
}
</script>
