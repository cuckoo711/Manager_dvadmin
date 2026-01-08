<template>
  <div class="log-viewer">
    <!-- 包裹 PerfectScrollbar -->
    <PerfectScrollbar class="log-scroll">
      <transition-group name="log-fade" tag="ul">
        <li
            v-for="(logItem, index) in reversedLogs"
            :key="index"
            class="log-item"
        >
          <span class="log-time" v-if="extractTime(logItem)">
            [ {{ extractTime(logItem) }} ]
          </span>
          <span class="log-content">
            {{ extractContent(logItem) }}
          </span>
        </li>
      </transition-group>
    </PerfectScrollbar>
  </div>
</template>

<script>
import { PerfectScrollbar } from 'vue3-perfect-scrollbar';

export default {
  name: 'LogViewer',
  components: {
    PerfectScrollbar,
  },
  props: {
    logs: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      classOption: {
        step: 0.6,
        limitMoveNum: 10,
        hoverStop: true,
        direction: 1,
        openWatch: true,
      },
    };
  },
  computed: {
    reversedLogs() {
      return this.logs.slice().reverse();
    },
  },
  methods: {
    extractTime(log) {
      const timeRegex = /^\[([^\]]+)]/; // 匹配 [时间] 格式
      const match = log.match(timeRegex);
      return match ? match[1] : null;
    },
    extractContent(log) {
      const timeRegex = /^\[([^\]]+)]/; // 匹配 [时间] 格式
      return log.replace(timeRegex, '').trim();
    },
  },
};
</script>

<style scoped>
.log-viewer {
  height: 100%;
  overflow: hidden; /* 防止滚动条溢出 */
}

.log-scroll {
  height: 100%;
  overflow: auto;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.log-item {
  padding: 5px;
  border-bottom: 1px solid #ccc;
}

.log-fade-enter-active, .log-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s; /* 动画时间 */
}

.log-fade-enter, .log-fade-leave-to /* .log-fade-leave-active in <2.1.8 */
{
  opacity: 1;
  transform: translateY(0); /* 进入时恢复到正常位置 */
}

.log-time {
  color: #00a0e1;
  margin-right: 10px;
}

.log-content {
  color: black;
}
</style>
