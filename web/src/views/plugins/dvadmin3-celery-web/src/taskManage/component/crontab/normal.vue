<template>
  <div class="popup-result maxh">
    <p class="title">常用cron表达式例子</p>
    <ul class="popup-result-scroll">
      <li v-for="(item, index) in cronList" :key="index">
        ({{ index + 1 }})
        <span class="ftcolor">{{ item.ex }}</span>
        {{ item.label }}
      </li>
    </ul>
  </div>
</template>
<script setup lang="ts">
import {ref,watch,computed} from 'vue';
interface CronData {
  ex?: string;
  label?: string;
}
const cronList = ref<CronData[]>([
  // { ex: "0/2 * * * * ?", label: "表示每2秒 执行任务" },
  { ex: "0/2 * * * ?", label: "表示每2分钟 执行任务" },
  { ex: "0 2 1 * ?", label: "表示在每月的1日的凌晨2点调整任务" },
  {
    ex: "15 10 ? * 1-5",
    label: "表示周一到周五每天上午10:15执行作业",
  },
  {
    ex: "15 10 ? 6L 2002-2006",
    label: "表示2002-2006年的每个月的最后一个星期五上午10:15执行作",
  },
  { ex: "0 10,14,16 * * ?", label: "每天上午10点，下午2点，4点" },
  { ex: "0/30 9-17 * * ?", label: "朝九晚五工作时间内每半小时" },
  { ex: "0 12 ? * 3", label: "表示每个星期三中午12点" },
  { ex: "0 12 * * ?", label: "每天中午12点触发" },
  { ex: "15 10 ? * *", label: "每天上午10:15触发" },
  { ex: "15 10 * * ?", label: "每天上午10:15触发" },
  { ex: "15 10 * * ? 2005", label: "2005年的每天上午10:15触发" },
  {
    ex: "0/5 14 * * ?",
    label: "在每天下午2点到下午2:00期间的每5分钟触发",
  },
  {
    ex: "0/5 14,18 * * ?",
    label: "在每天下午2点到2:55期间和下午6点到6:55期间的每5分钟触发",
  },
  {
    ex: "0-5 14 * * ?",
    label: "在每天下午2点到下午2:05期间的每1分钟触发",
  },
  {
    ex: "10,44 14 ? 3 3",
    label: "每年三月的星期三的下午2:10和2:44触发",
  },
  { ex: "15 10 ? * 1-5", label: "周一至周五的上午10:15触发" },
  { ex: "15 10 15 * ?", label: "每月15日上午10:15触发" },
  { ex: "15 10 L * ?", label: "每月最后一日的上午10:15触发" },
  { ex: "15 10 ? * 6L", label: "每月的最后一个星期五上午10:15触发" },
  {
    ex: "15 10 ? * 6L 2002-2005",
    label: "2002年至2005年的每月的最后一个星期五上午10:15触发",
  },
  {
    ex: "15 10 ? * 6#3",
    label: "每月的第三个星期五上午10:15触发",
  },
]);
</script>
<style>
.maxh {
  height: 200px;

  overflow-y: scroll;
}
.ftcolor {
  color: var(--el-color-primary);
}
</style>
