<template>
  <div class="layout-navbars-breadcrumb-user-news">
    <div class="head-box">
      <div class="head-box-title">{{ $t('message.user.newTitle') }}</div>
      <div class="head-box-btn" v-if="messageCenter.unread > 0" @click="onAllReadClick">{{
          $t('message.user.newBtn')
        }}
      </div>
      <div class="head-box-btn" v-else @click="ElMessage.warning('都说没有新消息了，还点')">
        {{ $t('message.user.newBtnNo') }}
      </div>
    </div>
    <div class="content-box">
      <template v-if="state.newsList.length > 0">
        <div class="content-box-item" v-for="(v, k) in state.newsList" :key="k">
          <div>{{ v?.title }}</div>
          <div class="content-box-msg">
            <div v-html="v?.content"></div>
          </div>
          <div class="content-box-time">{{ v?.create_datetime }}</div>
        </div>
      </template>
      <el-empty :description="$t('message.user.newDesc')" v-else></el-empty>
    </div>
    <div class="foot-box" @click="onGoToGiteeClick" v-if="state.newsList.length > 0">{{
        $t('message.user.newGo')
      }}
    </div>
  </div>
</template>

<!-- userNews.vue -->
<script setup lang="ts" name="layoutBreadcrumbUserNews">
import {onMounted, reactive} from 'vue';
import {request} from "/@/utils/service";
import {messageCenterStore} from '/@/stores/messageCenter'; // 导入 messageCenterStore
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";

// 初始化 messageCenterStore
const messageCenter = messageCenterStore();

// 定义响应式状态
const state = reactive({
  newsList: [] as any,
});

// 全部已读点击
const onAllReadClick = () => {
  request({
    url: '/api/system/message_center/read_all_msg/',
    method: 'get',
  }).then((res: any) => {
    if (res.data.status) {
      ElMessage.success("已全部标记为已读");
      messageCenter.setUnread(0); // 更新未读消息数为0
      state.newsList = []; // 清空当前的消息列表
    } else {
      ElMessage.warning("暂无新消息");
    }
  }).catch(() => {
    ElMessage.error("操作失败，请重试");
  });
};

// 前往通知中心点击
const router = useRouter();
const onGoToGiteeClick = () => {
  router.push('/messageCenter');
};

// 获取最新消息
const getLastMsg = () => {
  request({
    url: '/api/system/message_center/get_newest_msg/',
    method: 'get',
    params: {}
  }).then((res: any) => {
    const {data} = res;
    if (data) {
      state.newsList = [data];
    }
  }).catch(() => {
    ElMessage.error("获取消息失败");
  });
};

// 页面加载时获取消息
onMounted(() => {
  getLastMsg();
});
</script>


<style scoped lang="scss">
.layout-navbars-breadcrumb-user-news {
  .head-box {
    display: flex;
    border-bottom: 1px solid var(--el-border-color-lighter);
    box-sizing: border-box;
    color: var(--el-text-color-primary);
    justify-content: space-between;
    height: 35px;
    align-items: center;

    .head-box-btn {
      color: var(--el-color-primary);
      font-size: 13px;
      cursor: pointer;
      opacity: 0.8;

      &:hover {
        opacity: 1;
      }
    }
  }

  .content-box {
    font-size: 13px;

    .content-box-item {
      padding-top: 12px;

      &:last-of-type {
        padding-bottom: 12px;
      }

      .content-box-msg {
        color: var(--el-text-color-secondary);
        margin-top: 5px;
        margin-bottom: 5px;
      }

      .content-box-time {
        color: var(--el-text-color-secondary);
      }
    }
  }

  .foot-box {
    height: 35px;
    color: var(--el-color-primary);
    font-size: 13px;
    cursor: pointer;
    opacity: 0.8;
    display: flex;
    align-items: center;
    justify-content: center;
    border-top: 1px solid var(--el-border-color-lighter);

    &:hover {
      opacity: 1;
    }
  }

  :deep(.el-empty__description p) {
    font-size: 13px;
  }
}
</style>
