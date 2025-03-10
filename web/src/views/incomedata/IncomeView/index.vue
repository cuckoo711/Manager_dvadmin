<template>
  <fs-page>
    <el-main style="height: 100%">
      <el-card style="height: 100%">
        <div class="card-header">
          日期选择：
          <div class="block">
            <el-date-picker v-model="user_selection_time" type="date" placeholder="选择日期" size="default"/>
            <el-button type="primary" @click="servers_by_date_search">搜索</el-button>
            <el-button type="primary" @click="servers_by_date_reset">重置</el-button>
            <el-button type="success" @click="exportData">导出本页</el-button>
          </div>
        </div>
        <br/>
        <el-tabs type="border-card" style="height: 100%" class="tabs">
          <el-tab-pane label="昨日收入明细" style="height: 100%" lazy>
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="tableData.yesterday_income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                />
              </template>
            </el-auto-resizer>
          </el-tab-pane>
          <el-tab-pane label="前七日收入明细" style="height: 100%" lazy>
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="tableData.last_week_income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                />
              </template>
            </el-auto-resizer>
          </el-tab-pane>
          <el-tab-pane label="前30天收入明细" style="height: 100%" lazy>
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="tableData.last_month_income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                />
              </template>
            </el-auto-resizer>
          </el-tab-pane>
          <el-tab-pane label="本月收入明细" style="height: 100%" lazy>
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="tableData.this_month_income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                />
              </template>
            </el-auto-resizer>
          </el-tab-pane>
          <el-tab-pane label="上月收入明细" style="height: 100%" lazy>
            <el-auto-resizer>
              <template #default="{ height, width }">
                <el-table-v2
                    :expanded-row-keys="expandedRowKeys"
                    :columns="columns"
                    :data="tableData.current_month_income"
                    :width="width"
                    :height="height"
                    :expand-column-key="expandColumnKey"
                />
              </template>
            </el-auto-resizer>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-main>
  </fs-page>
</template>
<style lang="scss">
.el-tabs__content {
  height: 100%;
  overflow: auto
}

.el-card__body {
  height: calc(100% - 50px);
}
</style>
<script lang="ts" setup>
import {computed, onMounted, ref} from "vue";
import {exportIncome, getIncome, GetIncomeExport} from './crud'
import {errorMessage, successMessage} from "/@/utils/message"; //接口地址

const expandColumnKey = 'game'
const expandedRowKeys = ref<string[]>([])
const columns = [
  {dataKey: 'index', title: '序号', key: 'index', minWidth: 80, align: 'center'},
  {dataKey: 'game', title: '游戏名称', key: 'game', minWidth: 300},
  {dataKey: 'channel', title: '渠道', key: 'channel', minWidth: 100},
  {dataKey: 'research_name', title: '研发', key: 'research_name', minWidth: 100},
  {dataKey: 'recharge', title: '总流水', key: 'recharge', minWidth: 150},
  {dataKey: 'discount', title: '折扣', key: 'discount', minWidth: 150},
  {dataKey: 'after_folding', title: '折后总收入', key: 'after_folding', minWidth: 150},
  {dataKey: 'our_folding_income', title: '我方折后收入', key: 'our_folding_income', minWidth: 150},
  {dataKey: 'research_folding_income', title: '研发折后收入', key: 'research_folding_income', minWidth: 150},
  {dataKey: 'channel_tips', title: '渠道备注', key: 'channel_tips', minWidth: 150},
  {dataKey: 'research_tips', title: '研发备注', key: 'research_tips', minWidth: 150},
]

interface Income_detil {
  id: number;
  game: string;
  channel: string;
  recharge: string;
  main_body: string;
  discount: string;
  after_folding: string;
  our_folding_income: string;
  research_folding_income: string;
  channel_tips: string;
  research_tips: string;
  release_date: string;
  research_name: string;
  channel_company: string;
  research_company: string;
  our_ratio: string;
  research_ratio: string;
  slotting_ratio: string;
  our_income: string;
  research_income: string;
  hasChildren?: boolean;
  children?: Income_detil[];
}

interface TableData {
  yesterday_income: Income_detil[];
  last_week_income: Income_detil[];
  last_month_income: Income_detil[];
  current_month_income: Income_detil[];
  this_month_income: Income_detil[];
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

// 计算属性：获取当前日期并格式化为 YYYY-MM-DD
const currentDateTime = computed(() => {
  const now = new Date();
  return formatDate(now);
});

const user_selection_time = ref(currentDateTime.value);
const response_data = ref<TableData>({
  yesterday_income: [],
  last_week_income: [],
  last_month_income: [],
  current_month_income: [],
  this_month_income: [],
});

const tableData = ref<TableData>({
  yesterday_income: [],
  last_week_income: [],
  last_month_income: [],
  current_month_income: [],
  this_month_income: [],
});

function addParentId(data: any[]) {
  return data.map((item: any, topIdx: number) => {
    item.index = topIdx + 1;
    item.parentId = null;
    if (item.children) {
      item.children.forEach((child: any, childIdx: number) => {
        child.index = `${topIdx + 1}-${childIdx + 1}`;
        child.parentId = item.id;
      });
    }
    return item;
  });
}

// 初始化获取今日数据
onMounted(async () => {
  await servers_by_date_search();
});

const servers_by_date_search = async () => {
  try {
    const response = await getIncome({
      date: formatDate(user_selection_time.value),
    });

    if (response) {
      // 要处理的字段列表
      const fields = [
        'yesterday_income',
        'last_week_income',
        'last_month_income',
        'current_month_income',
        'this_month_income'
      ];

      // 对每个字段进行处理
      fields.forEach(field => {
        if (response[field]) {
          response[field] = addParentId(response[field]);
        }
      });

      // 更新表格数据
      tableData.value = response;
    } else {
      // 如果没有返回数据，则使用空数据
      response_data.value = {
        yesterday_income: [],
        last_week_income: [],
        last_month_income: [],
        current_month_income: [],
        this_month_income: [],
      };
      tableData.value = response_data.value;
    }
    console.log(tableData.value);
  } catch (error) {
    console.error("数据获取失败", error);
    // 如果发生错误，使用空数据
    tableData.value = response_data.value;
  }
};

// 日历重置操作
const servers_by_date_reset = async () => {
  user_selection_time.value = currentDateTime.value;
  await servers_by_date_search();
};

const exportData = async () => {
  let date: string = formatDate(user_selection_time.value);
  if (!date) {
    date = formatDate(currentDateTime.value);
  }
  // tab的索引
  let page_type = document.querySelector('.el-tabs__item.is-active')?.getAttribute('aria-controls');
  if (page_type) {
    page_type = page_type.toString().replace('pane-', '');
    const response = await exportIncome(
        date, page_type
    );
    if (response.status) {
      const filename = response.filename;
      const fileresponse = await GetIncomeExport(response.data);
      if (fileresponse) {
        const blob = new Blob([fileresponse.data], {type: fileresponse.headers["content-type"]});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        successMessage("导出成功");
      } else {
        errorMessage("导出失败");
      }
    } else {
      errorMessage("导出失败");
    }
  }
  console.log(`导出的日期：${date}，导出的tab页：${page_type}`);
}

</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
}

.demo-date-picker .block:last-child {
  border-right: none;
}

.title h2 {
  text-align: center;
}

.card-header .block {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
