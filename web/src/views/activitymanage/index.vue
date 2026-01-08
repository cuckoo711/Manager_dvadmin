<template>
  <fs-page>
    <el-container style="height: 100%;">
      <el-header>
        <el-form inline style="margin-top: 15px" v-model="searchForm"
                 label-width="auto">
          <el-form-item label="游戏名称">
            <el-select
                v-model="searchForm.selectedGame"
                filterable
                allow-create
                default-first-option
                placeholder="请选择一款游戏"
                @change="selectedGameChange"
                v-loading="gamesLoding"
            >
              <el-option v-for="game in games" :key="game" :value="game">
                {{ game }}
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="活动标题">
            <el-input
                v-model="searchForm.activity_name"
                placeholder="请输入活动标题"
                @change="selectedGameChange"
            />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input
                v-model="searchForm.keyword"
                placeholder="请输入关键词"
                @change="selectedGameChange"
            />
          </el-form-item>
          <el-form-item>
            <el-button-group>
              <el-button type="primary" @click="selectedGameChange">查询</el-button>
              <el-button @click="loadGame" type="primary">刷新</el-button>
              <el-button @click="resetSelection" type="primary">重置</el-button>
            </el-button-group>
          </el-form-item>
        </el-form>
      </el-header>
      <el-container style="height: calc(100% - 60px);">
        <el-main style="height: 100%;padding:0 10px">
          <el-table
              :data="tableData"
              style="width: 100%;height: 100%;"
              v-loading="activitiesLoding"
              border
              highlight-current-row
              @current-change="handleCurrentChange"
          >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="game_name" label="游戏名"></el-table-column>
            <el-table-column prop="activity_name" label="活动名称" show-overflow-tooltip></el-table-column>
          </el-table>
        </el-main>
        <el-aside width="60%" style="height: 100%;padding:0 10px">
          <el-card style="height: 100%;overflow: auto;" v-loading="activityDetailLoading" shadow="never">
            <template #header>
              <div>活动详情</div>
            </template>
            <div v-if="activityDetail">
              <p v-html="activityDetail"></p>
            </div>
            <div v-else>
              <p>请选择一项活动查看详情</p>
            </div>
          </el-card>
        </el-aside>
      </el-container>
    </el-container>
  </fs-page>
</template>

<script setup lang="ts">
import {onMounted, ref} from 'vue'
import {GetActivitiesByGameName, GetActivityContent, GetAllActivitiesGameNames} from '/@/views/activitymanage/api'

const gamesLoding = ref(false)
const activitiesLoding = ref(false)
const activityDetailLoading = ref(false)

const searchForm = ref({
  selectedGame: '',
  activity_name: '',
  keyword: '',
})
const games = ref<string[]>([])
const tableData = ref<any[]>([])
const activityDetail = ref<any>(null)

function formatActivityValue(value: string): string {
  if (!value) return '';

  // 使用正则表达式匹配数字、符号和中文/英文，并为不同的部分设置颜色
  let formattedValue = value.replace(/(\d+)|([^\w\s\u4e00-\u9fa5])|([a-zA-Z]+)/g, (match, p1, p2, p3) => {
    if (p1) {
      // 数字设置为蓝色
      return `<span style="color: blue;">${p1}</span>`;
    } else if (p2) {
      // 符号设置为红色
      return `<span style="color: red;">${p2}</span>`;
    } else if (p3) {
      // 英文不改变颜色，保留原样（默认是黑色）
      return `<span style="color: black;">${p3}</span>`;
    }
    return match; // 如果没有匹配到，返回原值
  });

  // 中文字符不需要更改，因为它们会被保留为默认颜色（黑色）

  // 将换行符转换为 <br> 标签，保留换行
  formattedValue = formattedValue.replace(/\n/g, '<br>');

  return formattedValue;
}


// 根据选择的游戏获取活动列表
async function selectedGameChange() {
  activitiesLoding.value = true
  const res = await GetActivitiesByGameName(
      searchForm.value.selectedGame,
      searchForm.value.activity_name,
      searchForm.value.keyword
  )
  tableData.value = res.activities || []
  activityDetail.value = null  // 切换游戏后清除详情
  activitiesLoding.value = false
}

const loadGame = async () => {
  gamesLoding.value = true
  const res = await GetAllActivitiesGameNames()
  gamesLoding.value = false
  games.value = res.game_names || []
  if (games.value.length > 0 && !searchForm.value.selectedGame) {
    searchForm.value.selectedGame = ""
    await selectedGameChange()
  }
}

// 行选中事件时，调用接口获取详细信息
async function handleCurrentChange(row: any) {
  activityDetailLoading.value = true
  if (!row) {
    activityDetail.value = null
    activityDetailLoading.value = false
    return
  }
  const res = await GetActivityContent(row.id)
  activityDetail.value = formatActivityValue(res.activity_value || '');  // 格式化内容
  activityDetailLoading.value = false
}

async function resetSelection() {
  searchForm.value.selectedGame = ''
  searchForm.value.activity_name = ''
  searchForm.value.keyword = ''
  tableData.value = []
  activityDetail.value = null
  await loadGame()
}

onMounted(() => {
  loadGame()
})
</script>
