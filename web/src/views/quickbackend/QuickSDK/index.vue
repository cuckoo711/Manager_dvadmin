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
                  <el-button-group style="margin-left: 20px;">
                    <el-button
                        type="primary"
                        :disabled="!accountNameValid"
                        size="small"
                        @click="reloadGameList"
                    >
                      重载游戏列表
                    </el-button>
                    <el-button
                        type="primary"
                        :disabled="!accountNameValid"
                        size="small"
                        @click="refreshChannelList"
                    >
                      刷新渠道状态
                    </el-button>
                  </el-button-group>
                </div>
              </template>
              <el-table
                  :data="[{}]"
                  style="width: 100%"
              >
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
                          :key="game.id"
                          :label="game.gameName"
                          :value="game.id"
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
                    <el-button-group>
                      <el-button
                          type="primary"
                          :disabled="!accountNameValid"
                          @click="handleBatchSwitch"
                      >
                        立即执行
                      </el-button>
                      <el-button
                          type="primary"
                          :disabled="!accountNameValid"
                          @click="handleRegularBatchSwitch"
                      >
                        定时执行
                      </el-button>
                    </el-button-group>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-container>
    </div>
    <div :style="{height: 'calc(100% - 95px)'}">
      <el-table
          ref="channelTable"
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
    <el-dialog
        title="选择定时日期"
        v-model="dialogVisible"
        width="400"
        :before-close="handleCloseDialog"
    >
      <el-date-picker
          v-model="scheduledDate"
          type="date"
          placeholder="选择执行日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledDate"
          :shortcuts="shortcuts"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDateSelection">确定</el-button>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script>
import {
  GetChannelSuffix,
  GetGameList,
  GetUser,
  PushLog,
  SwitchGame,
  UpdateChannelStatus, UpdateRegularChannelStatus
} from "/@/views/quickbackend/QuickSDK/api";
import {ElMessage, ElDialog, ElDatePicker} from "element-plus";
import {CircleCheckFilled, CircleCloseFilled} from "@element-plus/icons-vue";
import {ref} from 'vue'

export default {
  name: 'QuickSDK',
  components: {CircleCloseFilled, CircleCheckFilled},
  data() {
    return {
      dialogVisible: false, // 控制弹窗的显示
      scheduledDate: '', // 存储选择的定时日期
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
      ],
      shortcuts: [
        {
          text: '30天后',
          value: () => {
            const date = new Date();
            date.setDate(date.getDate() + 30);
            return date;
          }
        },
        {
          text: '60天后',
          value: () => {
            const date = new Date();
            date.setDate(date.getDate() + 60);
            return date;
          }
        },
        {
          text: '90天后',
          value: () => {
            const date = new Date();
            date.setDate(date.getDate() + 90);
            return date;
          }
        }
      ],
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
    debug: false,
    logtime() {
      const date = new Date();
      const options = {
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
    },
    async log(msg, push = true) {
      const log_message = this.logtime() + msg;
      if (push && !this.debug) {
        // 将日志推送到后端
        await PushLog(log_message);
      } else {
        console.log(log_message);
      }
    },
    getLog() {
      const account = this.accountName;
      const game = this.games.find(game => game.id === this.selectedGame).gameName;
      const operation = this.batchSwitchList.reduce((acc, group) => {
        const operation = group.options.find(option => option.value === this.batchSwitchType);
        if (operation) {
          acc = operation.type;
        }
        return acc;
      }, '');
      const channels = Object.values(this.multipleSelection).map(channel => channel.channel_name).join('，');
      return `【${account}】 对 【${game}】 进行了 【${operation}】 操作，涉及到的渠道有：【${channels}】`;
    },

    disabledDate(date) {
      return date.getTime() < Date.now(); // 禁用今天和之前的日期
    },
    // 弹窗关闭前的处理
    handleCloseDialog(done) {
      this.dialogVisible = false;
      done();
    },
    // 弹窗中的日期选择
    confirmDateSelection() {
      if (!this.scheduledDate) {
        ElMessage.error('请选择一个有效的日期');
        return;
      }

      // 将选择的日期传递给批量操作的处理逻辑
      this.handleRegularBatchSwitchConfirm(this.scheduledDate);
    },
    handleSelectionChange(val) {
      this.multipleSelection = val.reduce((acc, channel) => {
        acc[channel.channelId] = {
          channel_name: channel.channelName,
          no_login: channel.noLogin,
          no_pay: channel.noPay,
          no_register: channel.noRegister
        };
        return acc;
      }, {});
    },
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
      // 根据选择的游戏id，获取对应的productId
      if (!this.selectedGame) return;
      const game = this.games.find(game => game.id === this.selectedGame).productId;
      const response = await SwitchGame(game, this.channelSuffix);
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
    async handleRegularBatchSwitch() {
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
      // 弹出定时选择弹窗
      if (Object.keys(this.multipleSelection).length > 0) {
        const confirmedBatch = await this.confirmBatchOperation();
        if (confirmedBatch) {
          this.dialogVisible = true;
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
        await this.$refs.channelTable.toggleAllSelection();
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
          this.games.find(game => game.id === this.selectedGame).productId,
          this.batchSwitchType,
          this.multipleSelection
      );
      if (!response.status) {
        ElMessage.error(response.message);
        return;
      }
      ElMessage.success('批量操作成功');
      await this.log(this.getLog());
      await this.refreshChannelList();
      this.multipleSelection = {};
    },
    async handleRegularBatchSwitchConfirm(scheduledDate) {
      const gameName = this.games.find(game => game.id === this.selectedGame).gameName;
      const response = await UpdateRegularChannelStatus(
          this.games.find(game => game.id === this.selectedGame).productId,
          gameName,
          this.multipleSelection,
          this.getLog(),
          this.batchSwitchType,
          scheduledDate
      );

      if (!response.status) {
        ElMessage.error(response.message);
        return;
      }
      ElMessage.success('定时批量操作已提交');
      await this.log(`定时批量操作已提交，将在${scheduledDate}执行: ${this.getLog()}`);
      this.dialogVisible = false;
    },
  }
}
</script>
