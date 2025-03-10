<template>
  <el-config-provider :size="getGlobalComponentSize" :locale="getGlobalI18n">
    <router-view v-show="themeConfig.lockScreenTime > 1"/>
    <LockScreen v-if="themeConfig.isLockScreen"/>
    <Setings ref="setingsRef" v-show="themeConfig.lockScreenTime > 1"/>
    <CloseFull v-if="!themeConfig.isLockScreen"/>
  </el-config-provider>
</template>

<script setup lang="ts" name="app">
import {
  computed,
  defineAsyncComponent,
  nextTick,
  onBeforeMount,
  onBeforeUnmount,
  onMounted,
  onUnmounted,
  ref,
  watch
} from 'vue';
import {useRoute} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {storeToRefs} from 'pinia';
import {useTagsViewRoutes} from '/@/stores/tagsViewRoutes';
import {useThemeConfig} from '/@/stores/themeConfig';
import other from '/@/utils/other';
import {Local, Session} from '/@/utils/storage';
import mittBus from '/@/utils/mitt';
import setIntroduction from '/@/utils/setIconfont';
import {request} from '/@/utils/service';
// import disableDevtool from 'disable-devtool';
import websocket from '/@/utils/websocket';
import {ElNotification} from 'element-plus';
import * as jwtDecodeModule from 'jwt-decode';
import {messageCenterStore} from '/@/stores/messageCenter';
import {SystemConfigStore} from "/@/stores/systemConfig";

const LockScreen = defineAsyncComponent(() => import('/@/layout/lockScreen/index.vue'));
const Setings = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/setings.vue'));
const CloseFull = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/closeFull.vue'));

const {messages, locale} = useI18n();
const setingsRef = ref();
const route = useRoute();
const stores = useTagsViewRoutes();
const storesThemeConfig = useThemeConfig();
const {themeConfig} = storeToRefs(storesThemeConfig);

const jwtDecode = jwtDecodeModule.jwtDecode || jwtDecodeModule.default || jwtDecodeModule;

const getGlobalComponentSize = computed(() => other.globalComponentSize());
const getGlobalI18n = computed(() => messages.value[locale.value]);
const isDisableDevtool = computed(() => {
      return SystemConfigStore().systemConfig['base.disable_devtool'];
    })

onBeforeMount(() => {
  console.log('App.vue onBeforeMount, disableDevtool:', isDisableDevtool.value);
  // if (isDisableDevtool.value) {
  //   disableDevtool();
  // }
  setIntroduction.cssCdn();
  setIntroduction.jsCdn();
});

onMounted(() => {
  nextTick(() => {
    mittBus.on('openSetingsDrawer', () => setingsRef.value.openDrawer());

    if (Local.get('themeConfig')) {
      storesThemeConfig.setThemeConfig({themeConfig: Local.get('themeConfig')});
      document.documentElement.style.cssText = Local.get('themeConfigStyle');
    }

    if (Session.get('isTagsViewCurrenFull')) {
      stores.setCurrenFullscreen(Session.get('isTagsViewCurrenFull'));
    }
  });
});

onUnmounted(() => {
  mittBus.off('openSetingsDrawer');
});

watch(() => route.path, () => {
  other.useTitle();
  other.useFavicon();
  if (!websocket.websocket) {
    try {
      websocket.init(wsReceive);
    } catch (e) {
      console.log('websocket错误', e);
    }
  }
}, {deep: true});

const wsReceive = (message: any) => {
  const data = JSON.parse(message.data);
  const {unread} = data;
  const messageCenter = messageCenterStore();
  messageCenter.setUnread(unread);
  if (data.contentType === 'SYSTEM') {
    ElNotification({
      title: '系统消息',
      message: data.content,
      type: 'success',
      position: 'bottom-right',
      duration: 5000,
    });
  }
};

onBeforeUnmount(() => {
  websocket.close();
});

function setTokenRefreshInterval() {
  const refreshInterval = 60 * 1000; // 每分钟检查一次
  const bufferTime = 5 * 60 * 1000; // 提前5分钟刷新

  const refreshIntervalId = setInterval(() => {
    const refreshToken = Session.get('refreshToken');
    const tokenExpirationTime = Number(Session.get('tokenExpirationTime')) || Date.now();
    const currentTime = Date.now();

    if (!refreshToken || isNaN(tokenExpirationTime)) {
      clearInterval(refreshIntervalId);
      return;
    }

    if (tokenExpirationTime - currentTime < bufferTime) {
      refreshAccessToken().catch(() => {
        console.warn('Token 刷新失败，用户需要重新登录');
        window.location.href = '/login';
      });
    }
  }, refreshInterval);
}

async function refreshAccessToken() {
  const refreshToken = Session.get('refreshToken');

  if (!refreshToken) {
    console.warn('无有效的刷新令牌');
    return;
  }

  try {
    const response = await request({
      url: '/token/refresh/',
      method: 'POST',
      data: {refresh: refreshToken},
    });

    if (response.access) {
      Session.set('token', response.access);
    }
    if (response.refresh) {
      Session.set('refreshToken', response.refresh);
    }
    // 解析 JWT 获取过期时间
    try {
      const decodedToken: any = jwtDecode(response.access); // 解码 access token
      if (decodedToken && decodedToken.exp) {
        const tokenExpirationTime = decodedToken.exp * 1000; // 将秒转换为毫秒
        Session.set('tokenExpirationTime', String(tokenExpirationTime));
      } else {
        console.warn('未从 JWT 中获取到过期时间');
      }
    } catch (error) {
      console.error('JWT 解析失败', error);
    }
  } catch (error) {
    console.error('刷新 Token 请求失败', error);
    throw error;
  }
}

onMounted(() => {
  console.log('Token 刷新逻辑启动');
  setTokenRefreshInterval();
});

</script>
