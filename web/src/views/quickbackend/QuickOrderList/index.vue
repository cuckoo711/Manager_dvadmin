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
                    >
                      <el-option
                          v-for="game in games"
                          :key="game.key"
                          :label="game.gameName"
                          :value="game.productId"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                <!-- 查询输入框 -->
                <el-table-column
                    label="查询"
                    align="center"
                    header-align="center"
                    min-width="400"
                >
                  <template #default="scope">
                    <el-input
                        v-model="checkTxt"
                        placeholder="请输入查询内容"
                        class="input-with-select"
                    >
                      <template #prepend>
                        <el-select v-model="checkView" style="width: 100px">
                          <el-option
                              v-for="item in checkViewList"
                              :key="item.value"
                              :label="item.label"
                              :value="item.value"
                          />
                        </el-select>
                      </template>
                      <template #append>
                        <!--suppress JSValidateTypes -->
                        <el-button :icon="Search" @click="searchOrder" :disabled="isSearching"/>
                      </template>
                    </el-input>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-container>
    </div>
    <div>
      <el-card shadow="always" style="width: 100%">
        <el-tabs v-model="activeName">
          <!-- 订单列表 -->
          <el-tab-pane label="订单列表" name="first">
            <el-card shadow="always" style="width: 100%;">
              <el-table :data="tableData" style="width: 100%" height="600">
                <el-table-column prop="渠道" label="渠道" align="center"/>
                <el-table-column prop="区服" label="区服" align="center"/>
                <el-table-column prop="订单号" label="订单号" align="center" show-overflow-tooltip/>
                <el-table-column prop="用户 UID" label="用户 UID" align="center"/>
                <el-table-column prop="角色" label="角色" align="center"/>
                <el-table-column prop="金额" label="金额" align="center"/>
                <el-table-column prop="创建" label="创建时间" align="center"/>
                <el-table-column prop="渠道单号" label="渠道单号" align="center" show-overflow-tooltip/>
                <el-table-column prop="CP订单号" label="CP订单号" align="center" show-overflow-tooltip/>
                <el-table-column prop="商品ID" label="商品ID" align="center" show-overflow-tooltip/>
              </el-table>
            </el-card>
          </el-tab-pane>
          <!-- 汇总数据 -->
          <el-tab-pane label="订单汇总(每日总充值)" name="second">
            <el-card shadow="always" style="width: 100%; overflow: auto; height: auto">
              <el-table :data="summaryData" style="width: 100%" height="600">
                <el-table-column prop="渠道" label="渠道" align="center"/>
                <el-table-column prop="区服" label="区服" align="center"/>
                <el-table-column prop="用户 UID" label="用户 UID" align="center"/>
                <el-table-column prop="角色" label="角色" align="center"/>
                <el-table-column prop="创建日期" label="创建日期" align="center"/>
                <el-table-column prop="金额" label="金额" align="center"/>
              </el-table>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </fs-page>
</template>

<script>
import {
  GetGameList,
  GetUser,
} from "/@/views/quickbackend/QuickSDK/api";
import {ElMessage} from "element-plus";
import {CircleCheckFilled, CircleCloseFilled, Search} from "@element-plus/icons-vue"; // 包含 Search
import {ref} from 'vue'
import {GetPlayerDataByAny} from "/@/views/quickbackend/QuickOrderList/api";

export default {
  name: 'QuickOrderList',
  components: {CircleCloseFilled, CircleCheckFilled, Search},
  data() {
    return {
      Search,
      isCollapsed: [],
      accountName: '',
      selectedGame: ref(''),
      checkView: ref('roleName'),
      checkTxt: ref(''),
      games: [],
      activeName: 'first',
      checkViewList: [
        {label: '订单号', value: 'orderNo'},
        {label: 'CP订单号', value: 'cpOrderNo'},
        {label: '渠道单号', value: 'channelOrderNo'},
        {label: '角色名', value: 'roleName'},
        {label: '用户 UID', value: 'uid'},
        {label: '用户名称', value: 'username'},
        {label: '区服', value: 'server'},
      ],
      isSearching: false, // 新增状态变量，控制查询按钮
      tableData: [], // 订单详细数据
      summaryData: [] // 汇总数据
    };
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
    async searchOrder() {
      try {
        if (!this.accountNameValid) {
          ElMessage.error('请先在Quick操作账号中添加账号');
          return;
        }
        if (!this.selectedGame) {
          ElMessage.error('请选择游戏');
          return;
        }
        if (!this.checkTxt) {
          // 询问是否确认不输入查询条件，如果是则继续查询，否则返回
          const confirm = await this.$confirm('未输入查询条件, 数据量可能过大造成页面卡顿, 是否继续查询?', '提示', {
            confirmButtonText: '继续查询',
            cancelButtonText: '返回',
            type: 'warning'
          });
          if (confirm !== 'confirm') {
            return;
          }
        }
        this.isSearching = true;
        const loadingMessage = ElMessage({
          message: '正在查询,请稍候(约 30 秒)...',
          type: 'info',
          showClose: false,
          duration: 0,
        });
        const response = await GetPlayerDataByAny(
            this.selectedGame,
            this.checkView,
            this.checkTxt
        );
        loadingMessage.close();
        if (response.status) {
          ElMessage.success('查询成功');
          this.tableData = response.data;
          this.summaryData = response.mix_data;
        } else {
          this.tableData = [];
          this.summaryData = [];
          ElMessage.error(response.message);
        }
      } catch (e) {
        this.tableData = [];
        this.summaryData = [];
        ElMessage.error('查询失败');
      } finally {
        this.isSearching = false;
      }
    }
  }
}
</script>
