<template>
	<el-config-provider :size="getGlobalComponentSize" :locale="getGlobalI18n">
		<!-- v-show="themeConfig.lockScreenTime > 1" -->
		<router-view v-show="themeConfig.lockScreenTime > 1" />
		<LockScreen v-if="themeConfig.isLockScreen" />
		<Setings ref="setingsRef" v-show="themeConfig.lockScreenTime > 1" />
		<CloseFull v-if="!themeConfig.isLockScreen" />
<!--		<Upgrade v-if="getVersion" />-->
	</el-config-provider>
</template>

<script setup lang="ts" name="app">
import { defineAsyncComponent, computed, ref, onBeforeMount, onMounted, onUnmounted, nextTick, watch, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
import { useThemeConfig } from '/@/stores/themeConfig';
import other from '/@/utils/other';
import { Local, Session } from '/@/utils/storage';
import mittBus from '/@/utils/mitt';
import setIntroduction from '/@/utils/setIconfont';
import {request} from '/@/utils/service';
import * as jwtDecodeModule from 'jwt-decode';

// 引入组件
const LockScreen = defineAsyncComponent(() => import('/@/layout/lockScreen/index.vue'));
const Setings = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/setings.vue'));
const CloseFull = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/closeFull.vue'));
const Upgrade = defineAsyncComponent(() => import('/@/layout/upgrade/index.vue'));
const jwtDecode = jwtDecodeModule.jwtDecode || jwtDecodeModule.default || jwtDecodeModule;

import { ElMessageBox, ElNotification, NotificationHandle } from 'element-plus';
import { useCore } from '/@/utils/cores';
// 定义变量内容
const { messages, locale } = useI18n();
const setingsRef = ref();
const route = useRoute();
const stores = useTagsViewRoutes();
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
import websocket from '/@/utils/websocket';
const core = useCore();
const router = useRouter();
// 获取版本号
const getVersion = computed(() => {
	let isVersion = false;
	if (route.path !== '/login') {
		// @ts-ignore
		if ((Local.get('version') && Local.get('version') !== __VERSION__) || !Local.get('version')) isVersion = true;
	}
	return isVersion;
});
// 获取全局组件大小
const getGlobalComponentSize = computed(() => {
	return other.globalComponentSize();
});
// 获取全局 i18n
const getGlobalI18n = computed(() => {
	return messages.value[locale.value];
});
// 设置初始化，防止刷新时恢复默认
onBeforeMount(() => {
	// 设置批量第三方 icon 图标
	setIntroduction.cssCdn();
	// 设置批量第三方 js
	setIntroduction.jsCdn();
});
// 页面加载时
onMounted(() => {
	nextTick(() => {
		// 监听布局配'置弹窗点击打开
		mittBus.on('openSetingsDrawer', () => {
			setingsRef.value.openDrawer();
		});
    // 设置皮肤缓存版本，每次更新版本可以所有用户清空缓存
    const themeConfigVersion = '1.0.0'
		// 获取缓存中的布局配置
    if (Local.get('themeConfigVersion') !== themeConfigVersion) {
        Local.clear();
        Local.set('themeConfigVersion', themeConfigVersion);
	      window.location.reload();
        return
    }
		if (Local.get('themeConfig')) {
			storesThemeConfig.setThemeConfig({ themeConfig: Local.get('themeConfig') });
			document.documentElement.style.cssText = Local.get('themeConfigStyle');
		}
		// 获取缓存中的全屏配置
		if (Session.get('isTagsViewCurrenFull')) {
			stores.setCurrenFullscreen(Session.get('isTagsViewCurrenFull'));
		}
	});
});
// 页面销毁时，关闭监听布局配置/i18n监听
onUnmounted(() => {
	mittBus.off('openSetingsDrawer', () => {});
});
// 监听路由的变化，设置网站标题
watch(
	() => route.path,
	() => {
		other.useTitle();
    other.useFavicon();
    if (!websocket.websocket) {
      //websockt 模块
      try {
        websocket.init(wsReceive)
      } catch (e) {
        console.log('websocket错误');
      }
    }
	},
	{
		deep: true,
	}
);

// websocket相关代码
import { messageCenterStore } from '/@/stores/messageCenter';
const wsReceive = (message: any) => {
	const data = JSON.parse(message.data);
	const { unread } = data;
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
	} else if (data.contentType === 'Content') {
		ElMessageBox.confirm(data.content, data.notificationTitle, {
			confirmButtonText: data.notificationButton,
      dangerouslyUseHTMLString: true,
			cancelButtonText: '关闭',
			type: 'info',
			closeOnClickModal: false,
		}).then(() => {
        ElMessageBox.close();
				const path = data.path;
        if (route.path === path) {
          core.bus.emit('onNewTask', { name: 'onNewTask' });
        } else {
          router.push({ path});
        }
			})
			.catch(() => {});
	}

};
onBeforeUnmount(() => {
	// 关闭连接
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
