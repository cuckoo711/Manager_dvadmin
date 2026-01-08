<template>
  <fs-page>
    <el-main style="height: 100%">
      <el-card style="height: 100%">
        <div class="card-header">
          选择日期：
          <div class="block">
            <el-date-picker v-model="user_selection_time" type="date" placeholder="选择日期" size="default"
                            :disabled-date="disableFutureDate"/>
            <el-button type="primary" @click="servers_by_date_search">搜索</el-button>
            <el-button type="primary" @click="servers_by_date_reset">重置</el-button>
            <!--              <el-button type="primary" @click="manual_update">手动更新</el-button>-->
          </div>
        </div>
        <br/>
        <el-tabs type="border-card" style="height: calc(100% - 100px)">
          <el-tab-pane label="参考收入">
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="data.income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                    @column-sort="onSort"
                    :sort-by="sortState"
                >
                </el-table-v2>
              </template>
            </el-auto-resizer>
          </el-tab-pane>
          <el-tab-pane label="版号">
            <el-table :data="data.banhao"
                      :default-sort="{ prop: '前一日总充值', order: 'descending' }">
              <el-table-column type="index" fixed width="100" label="No."/>
              <el-table-column prop="版号" label="版号" sortable fixed align="center"
                               show-overflow-tooltip/>
              <el-table-column prop="last1day_recharge" label="前一日总充值" sortable align="center"/>
              <el-table-column prop="last7days_recharge" label="前七日内总充值" sortable align="center"/>
              <el-table-column prop="last30days_recharge" label="前三十日内总充值" sortable align="center"/>
              <el-table-column prop="yesterday_actives" label="昨日活跃总用户（人）" sortable align="center"/>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="服务器">
            <el-table :data="data.instance">
              <el-table-column type="index" fixed width="100" label="No."/>
              <el-table-column prop="实例名称" label="实例名称" fixed align="center" min-width="150"/>
              <el-table-column prop="实例ID" label="实例ID" align="center" min-width="150"
                               show-overflow-tooltip/>
              <el-table-column prop="状态" label="状态" sortable align="center"/>
              <el-table-column prop="CPU" label="CPU" sortable align="center" width="100"/>
              <el-table-column prop="内存" label="内存" sortable align="center" width="100"/>
              <el-table-column prop="主IPv4地址" label="主IPv4地址" sortable align="center"/>
              <el-table-column prop="到期时间" label="到期时间" sortable align="center" width="200"/>
              <el-table-column prop="所属账号" label="所属账号" sortable align="center" width="120"/>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-main>
    <template #footer>
      <div class="flex items-center"
           style="justify-content: center;height: 100%;background-color: var(--el-color-primary-light-7);">
        {{ watermarkContent }}
      </div>
    </template>
  </fs-page>
</template>

<style lang="scss">
.el-table {
  width: 100%;
  height: calc(100%)
}

.el-tab-pane {
  height: 100%;
  padding: 0
}

.el-tabs__content {
  height: auto;
}

.el-card__body {
  height: 100%;
  padding-bottom: 0
}
</style>

<script lang="tsx" setup>
import {computed, onMounted, ref} from "vue";
import {getReport} from "/@/views/dailyreport/DailyView/api";
import type {HeaderCellSlotProps, SortBy} from 'element-plus'
import {TableV2SortOrder} from 'element-plus'
import {Filter} from '@element-plus/icons-vue'

const disableFutureDate = (date: Date) => {
  const today = new Date();
  today.setHours(0, 10, 0, 0); // 设置为当天的00:00:00，确保比较日期不受时分秒影响
  return date > today;
};
const expandedRowKeys = ref<string[]>([])
const expandColumnKey = 'game_name'
const popoverRef = ref()
const shouldFilter = ref('')
const backupData = ref()

const onReset = () => {
  shouldFilter.value = ''
  onFilter(true)
}

const onFilter = (hide: boolean = false) => {
  if (hide) {
    popoverRef.value.hide()
  }
  if (shouldFilter.value) {
    data.value.income = backupData.value.income.filter((item: any) => item.game_name.includes(shouldFilter.value))
  } else {
    data.value.income = backupData.value.income
  }
}

const columns = [
  {dataKey: 'index', title: '序号', key: 'index', minWidth: 80, align: 'center'},
  {
    dataKey: 'game_name',
    title: '游戏名称',
    key: 'game_name',
    minWidth: 400,
    headerCellRenderer: (props: HeaderCellSlotProps) => {
      return (
          <div class="flex items-center justify-center">
            <span>{props.column.title}</span>
            <el-popover ref={popoverRef} trigger="click" {...{width: 200}}>
              {{
                default: () => (
                    <div>
                      <el-input v-model={shouldFilter.value} placeholder="输入筛选条件" onInput={() => onFilter(false)}/>
                      <el-button-group style="margin-top: 10px">
                        <el-button onClick={() => onFilter(true)}>
                          筛选
                        </el-button>
                        <el-button onClick={onReset}>
                          重置
                        </el-button>
                      </el-button-group>
                    </div>
                ),
                reference: () => (
                    <el-icon class="cursor-pointer">
                      <Filter/>
                    </el-icon>
                ),
              }}
            </el-popover>
          </div>
      )
    }

  },
  {
    dataKey: 'include',
    title: '数据跨度',
    key: 'include',
    minWidth: 150,
    align: 'center',
    cellRenderer: ({cellData: include}) => (
        <el-tooltip content={getTooltipContent(include)} placement="left">
          <el-tag>{include}</el-tag>
        </el-tooltip>),
  },
  {
    dataKey: 'channels_number',
    title: '渠道数量',
    key: 'channels_number',
    minWidth: 125,
    align: 'center',
    sortable: true
  },
  {dataKey: 'payments', title: '付费用户', key: 'payments', minWidth: 125, align: 'center', sortable: true},
  {
    dataKey: 'subscribers',
    title: '累计用户',
    key: 'subscribers',
    minWidth: 125,
    align: 'center',
    sortable: true,
    cellRenderer: ({cellData: subscribers}) => (
        <el-tag type={getYesterdayActivesStyle({cellData: subscribers})} v-show={subscribers}>{subscribers}</el-tag>
    ),
  },
  {
    dataKey: 'recharge',
    title: '累计充值',
    key: 'recharge',
    minWidth: 125,
    align: 'center',
    sortable: true,
    cellRenderer: ({cellData: recharge}) => (
        <el-tag type={getRechargeStyle({cellData: recharge})} v-show={recharge}>{recharge}</el-tag>
    ),
  },
  {
    dataKey: 'online_days',
    title: '上线天数',
    key: 'online_days',
    minWidth: 125,
    align: 'center',
    sortable: true,
    cellRenderer: ({cellData: online_days}) => (
        <el-tag type={getOnlinDaysStyle({cellData: online_days})} v-show={online_days}>{online_days}</el-tag>
    ),
  },
  {
    dataKey: 'yesterday_actives',
    title: '昨日活跃',
    key: 'yesterday_actives',
    minWidth: 125,
    align: 'center',
    sortable: true,
    cellRenderer: ({cellData: yesterday_actives}) => (
        <el-tag type={getYesterdayActivesStyle({cellData: yesterday_actives})}
                v-show={yesterday_actives}>{yesterday_actives}</el-tag>
    ),
  },
]

function getRechargeStyle({cellData}: { cellData: number }) {
  if (cellData < 100) {
    return 'danger';
  } else if (cellData < 500) {
    return 'warning';
  } else {
    return 'success';
  }
}

function getYesterdayActivesStyle({cellData}: { cellData: number }) {
  if (cellData < 30) {
    return 'danger';
  } else if (cellData < 60) {
    return 'warning';
  } else {
    return 'success';
  }
}

function getOnlinDaysStyle({cellData}: { cellData: number }) {
  if (cellData < 30) {
    return 'success';
  } else if (cellData < 60) {
    return 'warning';
  } else {
    return 'danger';
  }
}

const watermarkContent = computed(() => {
  const user_selection_time_obj = new Date(user_selection_time.value).getTime();
  const dateobj = {
    year: new Date(user_selection_time_obj).getFullYear(),
    month: new Date(user_selection_time_obj).getMonth() + 1,
    day: new Date(user_selection_time_obj).getDate(),
  };
  return `当前页面数据截止至 ${dateobj.year}年${dateobj.month}月${dateobj.day}日 00时05分00秒`;
});

function getTooltipContent(include: string): string {
  // 将用户选择的日期转换为日期对象再减一天
  const user_selection_time_obj = new Date(user_selection_time.value).getTime() - 24 * 60 * 60 * 1000;
  if (include === '昨日') {
    return `${formatDate(user_selection_time_obj)} 00:00:00 ~ ${formatDate(user_selection_time_obj)} 23:59:59`;
  } else if (include === '前七日') {
    const seven_days_ago = new Date(user_selection_time_obj - 7 * 24 * 60 * 60 * 1000);
    return `${formatDate(seven_days_ago)} 00:00:00 ~ ${formatDate(user_selection_time_obj)} 23:59:59`;
  } else if (include === '前三十日') {
    const thirty_days_ago = new Date(user_selection_time_obj - 30 * 24 * 60 * 60 * 1000);
    return `${formatDate(thirty_days_ago)} 00:00:00 ~ ${formatDate(user_selection_time_obj)} 23:59:59`;
  } else if (include === '当前月') {
    const first_day_of_month = new Date(user_selection_time_obj);
    first_day_of_month.setDate(1);
    return `${formatDate(first_day_of_month)} 00:00:00 ~ ${formatDate(user_selection_time_obj)} 23:59:59`;
  } else if (include === '上个月') {
    const first_day_of_month = new Date(user_selection_time_obj).setDate(1);
    const last_daty_of_last_month = new Date(first_day_of_month - 24 * 60 * 60 * 1000);
    const first_day_of_last_month = new Date(last_daty_of_last_month).setDate(1);
    return `${formatDate(first_day_of_last_month)} 00:00:00 ~ ${formatDate(last_daty_of_last_month)} 23:59:59`;
  }
  return include;
}

// 方法：将日期转换为 YYYY-MM-DD 格式的字符串
function formatDate(date: Date | string | number) {
  if (!date) return "";
  const d = new Date(date);
  const year = d.getFullYear();
  const month = `${d.getMonth() + 1}`.padStart(2, "0");
  const day = `${d.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const sortState = ref<SortBy>({
  key: 'column-0',
  order: TableV2SortOrder.ASC,
})

const onSort = (sortBy: SortBy) => {
  console.log(sortBy)
  data.value.income = data.value.income.slice().sort((a, b) => {
    const key = sortBy.key
    if (sortBy.order === TableV2SortOrder.ASC) {
      return a[key] - b[key]
    } else {
      return b[key] - a[key]
    }
  })
  sortState.value = sortBy
}
// 计算属性：获取当前日期并格式化为 YYYY-MM-DD
const currentDateTime = computed(() => {
  const now = new Date();
  return formatDate(now);
});

const user_selection_time = ref(currentDateTime.value);
const data = ref<{
  banhao: any[],
  income: any[],
  instance: any[]
}>({banhao: [], income: [], instance: []});

// 初始化获取今日数据
onMounted(async () => {
  try {
    await getReport().then((response: any) => {
      if (response) {
        data.value = response;
        backupData.value = JSON.parse(JSON.stringify(response));
      } else {
        data.value = {banhao: [], income: [], instance: []};
        backupData.value = {banhao: [], income: [], instance: []};
      }
    });
  } catch (error) {
    console.error("请求数据失败:", error);
  }
});

const servers_by_date_search = async () => {
      try {
        await getReport({date: formatDate(user_selection_time.value),}).then((response: any) => {
          if (response) {
            data.value = response;
          } else {
            data.value = {banhao: [], income: [], instance: []};
          }
        });
      } catch
          (error) {
        console.error("请求数据失败:", error);
      }
    }
;

// 日历重置操作
const servers_by_date_reset = async () => {
  user_selection_time.value = currentDateTime.value;
  await getReport().then((response: any) => {
    if (response) {
      data.value = response;
    } else {
      data.value = {banhao: [], income: [], instance: []};
    }
  });
};
const getIncomeSummary = (param: { columns: any; data: any }) => {
  const {columns, data} = param;
  const sums: any[] = [];
  columns.forEach((column: any, index: number) => {
    if (index === 0) {
      sums[index] = '合计';
      return;
    }
    if (['online_days'].includes(column.property)) {
      sums[index] = ''; // 不需要合计的数据列
      return;
    }
    const values = data.map((item: any) => Number(item[column.property]));
    if (!values.every((value: any) => isNaN(value))) {
      sums[index] = values.reduce((prev: any, curr: any) => {
        const value = Number(curr);
        if (!isNaN(value)) {
          return prev + curr;
        } else {
          return prev;
        }
      }, 0);
      if (['yesterday_actives'].includes(column.property)) {
        sums[index] = sums[index].toFixed(0);
      } else {
        sums[index] = sums[index].toFixed(2); // 保留两位小数
      }
    } else {
      sums[index] = '';
    }
  });
  return sums;
};
</script>