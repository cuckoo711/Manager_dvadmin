<template>
  <div>
    <el-tabs type="border-card">

      <el-tab-pane label="分钟" v-if="shouldHide('min')">
        <CrontabMin
          @update="updateCrontabValue"
          :check="checkNumber"
          :cron="crontabValueObj"
          ref="cronmin"
        />
      </el-tab-pane>

      <el-tab-pane label="小时" v-if="shouldHide('hour')">
        <CrontabHour
          @update="updateCrontabValue"
          :check="checkNumber"
          :cron="crontabValueObj"
          ref="cronhour"
        />
      </el-tab-pane>

      <el-tab-pane label="日" v-if="shouldHide('day')">
        <CrontabDay
          @update="updateCrontabValue"
          :check="checkNumber"
          :cron="crontabValueObj"
          ref="cronday"
        />
      </el-tab-pane>

      <el-tab-pane label="月" v-if="shouldHide('month')">
        <CrontabMonth
          @update="updateCrontabValue"
          :check="checkNumber"
          :cron="crontabValueObj"
          ref="cronmonth"
        />
      </el-tab-pane>

      <el-tab-pane label="周" v-if="shouldHide('week')">
        <CrontabWeek
          @update="updateCrontabValue"
          :check="checkNumber"
          :cron="crontabValueObj"
          ref="cronweek"
        />
      </el-tab-pane>
    </el-tabs>

    <div class="popup-main">
      <div class="popup-result">
        <p class="title">时间表达式</p>
        <table>
          <thead>
            <tr>
              <th v-for="item of tabTitles" width="40" :key="item">
                {{ item }}
              </th>
              <th>Cron 表达式</th>
              <th>文字结果</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <span>{{ crontabValueObj.min }}</span>
              </td>
              <td>
                <span>{{ crontabValueObj.hour }}</span>
              </td>
              <td>
                <span>{{ crontabValueObj.day }}</span>
              </td>
              <td>
                <span>{{ crontabValueObj.month }}</span>
              </td>
              <td>
                <span>{{ crontabValueObj.week }}</span>
              </td>
              <td>
                <span>{{ crontabValueString }}</span>
              </td>
              <td>
                <span>{{ humanizeCronInChinese(crontabValueString) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <CrontabResult v-if="true" :expression="crontabValueString" />
      <Normal />
      <div class="pop_btn">
        <el-button size="small" type="primary" @click="submitFill">
          确定
        </el-button>
        <el-button size="small" type="warning" @click="clearCron">
          重置
        </el-button>
        <el-button size="small" @click="hidePopup">取消</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import CrontabMin from "./min.vue";
import CrontabHour from "./hour.vue";
import CrontabDay from "./day.vue";
import CrontabMonth from "./month.vue";
import CrontabWeek from "./week.vue";
import CrontabResult from "./result.vue";
import Normal from "./normal.vue";
import {computed, onMounted, ref, watch} from 'vue';
import { CrontabValueObj } from "./cron";
import {humanizeCronInChinese} from "cron-chinese";

const cronmin = ref();
const cronhour = ref();
const cronday = ref();
const cronweek = ref();
const cronmonth = ref();

//从父级接收数据，定义接口
interface Props {
  expression: string;
  hideComponent?: string;
}
const emit = defineEmits(["hide", "fill"]);
const propsData = defineProps<Props>();

const crontabValueObj = ref<CrontabValueObj>({
  min: "*",
  hour: "*",
  day: "*",
  month: "*",
  week: "*",
});
const tabTitles = ref<string[]>(["分钟", "小时", "日", "月", "周"]);
const tabActive = ref(0);

const crontabValueString = computed(() => {
  let obj = crontabValueObj.value;
  let str =
    obj.min +
    " " +
    obj.hour +
    " " +
    obj.day +
    " " +
    obj.month +
    " " +
    obj.week
  return str;
});

watch(
  crontabValueString,
  (newValue, oldValue) => {
    //resolveExp();
  },
  { immediate: true }
);
//   watch: {
//     expression: "resolveExp",
//     hideComponent(value) {
//       // 隐藏部分组件
//     },
//   },
// mounted: function () {
//   this.resolveExp();
// },

onMounted(() => {
  resolveExp();
});

function shouldHide(key: any) {
  if (propsData.hideComponent) return false;
  return true;
}
function resolveExp() {
  // 反解析 表达式
  if (propsData.expression) {
    let arr = propsData.expression.split(" ");
    if (arr.length >= 5) {
      //6 位以上是合法表达式
      let obj = {
        min: arr[0],
        hour: arr[1],
        day: arr[2],
        month: arr[3],
        week: arr[4],
      };
      crontabValueObj.value = {
        ...obj,
      };
      for (let i in obj) {
        if (obj[i]) changeRadio(i, obj[i]);
      }
    }
  } else {
    // 没有传入的表达式 则还原
    clearCron();
  }
}
// 由子组件触发，更改表达式组成的字段值
function updateCrontabValue(name: any, value: any, from: any) {
  // "updateCrontabValue", name, value, from;
  // crontabValueObj.value[name] = value;

  switch (name) {
    case "min":
      crontabValueObj.value.min = value;
      break;
    case "hour":
      crontabValueObj.value.hour = value;
      break;
    case "day":
      crontabValueObj.value.day = value;
      break;
    case "month":
      crontabValueObj.value.month = value;
      break;
    case "week":
      crontabValueObj.value.week = value;
      break;
  }
  // if (from && from !== name) {
  console.log(`来自组件 ${from} 改变了 ${name} ${value}`);
  changeRadio(name, value);
  // }
}
// 赋值到组件
function changeRadio(name: string, value: string) {
  let arr = [ "min", "hour", "month"],
    refName = "cron" + name,
    insValue;
  // if (!$refs[refName]) return;
  console.log("name=" + name + ",value=" + value);

  if (arr.includes(name)) {
    if (value === "*") {
      insValue = 1;
    } else if (typeof value === "string" && value.indexOf("-") > -1) {
      let indexArr = value.split("-");

      let _cronmin_cycle01 = cronmin.value.cycle01;
      let _cronhour_cycle01 = cronhour.value.cycle01;
      let _cronmonth_cycle01 = cronmonth.value.cycle01;

      if (name == "min") {
        isNaN(indexArr[0])
          ? (_cronmin_cycle01 = 0)
          : (_cronmin_cycle01 = indexArr[0]);
        cronmin.value.cycle02 = indexArr[1];
      } else if (name == "hour") {
        isNaN(indexArr[0])
          ? (_cronhour_cycle01 = 0)
          : (_cronhour_cycle01 = indexArr[0]);
        cronhour.value.cycle02 = indexArr[1];
      } else if (name == "month") {
        isNaN(indexArr[0])
          ? (_cronmonth_cycle01 = 0)
          : (_cronmonth_cycle01 = indexArr[0]);
        cronmonth.value.cycle02 = indexArr[1];
      }

      insValue = 2;
    } else if (typeof value === "string" && value.indexOf("/") > -1) {
      let indexArr = value.split("/");

      let _cronmin_average01 = cronmin.value.average01;
      let _cronhour_average01 = cronhour.value.average01;
      let _cronmonth_average01 = cronmonth.value.average01;

      if (name == "min") {
        isNaN(indexArr[0])
          ? (_cronmin_average01 = 0)
          : (_cronmin_average01 = indexArr[0]);
        cronmin.value.average02 = indexArr[1];
      } else if (name == "hour") {
        isNaN(indexArr[0])
          ? (_cronhour_average01 = 0)
          : (_cronhour_average01 = indexArr[0]);
        cronhour.value.average02 = indexArr[1];
      } else if (name == "month") {
        isNaN(indexArr[0])
          ? (_cronmonth_average01 = 0)
          : (_cronmonth_average01 = indexArr[0]);
        cronmonth.value.average02 = indexArr[1];
      }

      insValue = 3;
    } else {
      insValue = 4;
      //this.$refs[refName].checkboxList = value.split(",");

      if (name == "min") {
        cronmin.value.checkboxList = (value?.toString() ?? "").split(",");
      } else if (name == "hour") {
        cronhour.value.checkboxList = (value?.toString() ?? "").split(",");
      } else if (name == "month") {
        cronmonth.value.checkboxList = (value?.toString() ?? "").split(",");
      } else if (name == "day") {
        cronday.value.checkboxList = (value?.toString() ?? "").split(",");
      } else if (name == "week") {
        cronweek.value.checkboxList = (value?.toString() ?? "").split(",");
      }
    }
  } else if (name == "day") {
    if (value === "*") {
      insValue = 1;
    } else if (value == "?") {
      insValue = 2;
    } else if (value.indexOf("-") > -1) {
      let indexArr = value.split("-");
      isNaN(indexArr[0])
        ? (cronday.value.cycle01 = 0)
        : (cronday.value.cycle01 = indexArr[0]);
      cronday.value.cycle02 = indexArr[1];
      insValue = 3;
    } else if (value.indexOf("/") > -1) {
      let indexArr = value.split("/");
      isNaN(indexArr[0])
        ? (cronday.value.average01 = 0)
        : (cronday.value.average01 = indexArr[0]);
      cronday.value.average02 = indexArr[1];
      insValue = 4;
    } else if (value.indexOf("W") > -1) {
      let indexArr = value.split("W");
      isNaN(indexArr[0])
        ? (cronday.value.workday = 0)
        : (cronday.value.workday = indexArr[0]);
      insValue = 5;
    } else if (value === "L") {
      insValue = 6;
    } else {
      cronday.value.checkboxList = value.split(",");
      insValue = 7;
    }
  } else if (name == "week") {
    if (value === "*") {
      insValue = 1;
    } else if (value == "?") {
      insValue = 2;
    } else if (value.indexOf("-") > -1) {
      let indexArr = value.split("-");
      isNaN(indexArr[0])
        ? (cronweek.value.cycle01 = 0)
        : (cronweek.value.cycle01 = indexArr[0]);
      cronweek.value.cycle02 = indexArr[1];
      insValue = 3;
    } else if (value.indexOf("#") > -1) {
      let indexArr = value.split("#");
      isNaN(indexArr[0])
        ? (cronweek.value.average01 = 1)
        : (cronweek.value.average01 = indexArr[0]);
      cronweek.value.average02 = indexArr[1];
      insValue = 4;
    } else if (value.indexOf("L") > -1) {
      let indexArr = value.split("L");
      isNaN(indexArr[0])
        ? (cronweek.value.weekday = 1)
        : (cronweek.value.weekday = indexArr[0]);
      insValue = 5;
    } else {
      cronweek.value.checkboxList = value.split(",");
      insValue = 6;
    }
  }
  // this.$refs[refName].radioValue = insValue;

  if (name == "min") {
    cronmin.value.radioValue = insValue;
  } else if (name == "hour") {
    cronhour.value.radioValue = insValue;
  } else if (name == "month") {
    cronmonth.value.radioValue = insValue;
  } else if (name == "day") {
    cronday.value.radioValue = insValue;
  } else if (name == "week") {
    cronweek.value.radioValue = insValue;
  }
}
// 表单选项的子组件校验数字格式（通过-props传递）
function checkNumber(value: any, minLimit: any, maxLimit: any) {
  // 检查必须为整数
  value = Math.floor(value);
  if (value < minLimit) {
    value = minLimit;
  } else if (value > maxLimit) {
    value = maxLimit;
  }
  return value;
}
// 隐藏弹窗
function hidePopup() {
  emit("hide");
}
// 填充表达式
function submitFill() {
  emit("fill", crontabValueString.value);
  hidePopup();
}
function clearCron() {
  // 还原选择项
  ("准备还原");
  crontabValueObj.value = {
    min: "0",
    hour: "0",
    day: "*",
    month: "*",
    week: "*",
  };
  for (let j in crontabValueObj.value) {
    changeRadio(j, crontabValueObj.value[j]);
  }
}
</script>
<style scoped>
.pop_btn {
  text-align: center;
  margin-top: 20px;
}
.popup-main {
  position: relative;
  margin: 10px auto;
  background: #fff;
  border-radius: 5px;
  font-size: 12px;
  overflow: hidden;
}
.popup-title {
  overflow: hidden;
  line-height: 34px;
  padding-top: 6px;
  background: #f2f2f2;
}
.popup-result {
  box-sizing: border-box;
  line-height: 24px;
  margin: 25px auto;
  padding: 15px 10px 10px;
  border: 1px solid #ccc;
  position: relative;
}
.popup-result .title {
  position: absolute;
  top: -28px;
  left: 50%;
  width: 140px;
  font-size: 14px;
  margin-left: -70px;
  text-align: center;
  line-height: 30px;
  background: #fff;
}
.popup-result table {
  text-align: center;
  width: 100%;
  margin: 0 auto;
}
.popup-result table span {
  display: block;
  width: 100%;
  font-family: arial;
  line-height: 30px;
  height: 30px;
  white-space: nowrap;
  overflow: hidden;
  border: 1px solid #e8e8e8;
}
.popup-result-scroll {
  font-size: 12px;
  line-height: 24px;
  height: 10em;
  overflow-y: auto;
}
</style>
