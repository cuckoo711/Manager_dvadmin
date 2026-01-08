<template>
  <el-form size="small">
    <el-form-item>
      <el-radio v-model="radioValue" :label="1">
        周，允许的通配符[, - * ? / L #]
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="2">不指定</el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="3">
        周期从星期
        <el-select clearable v-model="cycle01">
          <el-option
            v-for="item in weekList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
        -
        <el-select clearable v-model="cycle02">
          <el-option
            v-for="item in weekList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="4">
        第
        <el-input-number v-model="average01" :min="1" :max="4" />
        周的星期
        <el-select clearable v-model="average02">
          <el-option
            v-for="(item, index) of weekList"
            :key="index"
            :label="item.value"
            :value="item.key"
          >
            {{ item.value }}
          </el-option>
        </el-select>
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="5">
        本月最后一个星期
        <el-select clearable v-model="weekday">
          <el-option
            v-for="(item, index) of weekList"
            :key="index"
            :label="item.value"
            :value="item.key"
          >
            {{ item.value }}
          </el-option>
        </el-select>
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="6">
        指定
        <el-select
          clearable
          v-model="checkboxList"
          placeholder="可多选"
          multiple
          style="width: 100%"
        >
          <el-option
            v-for="(item, index) of weekList"
            :key="index"
            :label="item.value"
            :value="String(item.key)"
          >
            {{ item.value }}
          </el-option>
        </el-select>
      </el-radio>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { defineExpose } from "vue";
import { CrontabValueObj, Week } from "./cron";
import {ref,watch,computed} from 'vue';
//从父级接收数据，定义接口
interface Props {
  cron: CrontabValueObj;
  check: Function;
}

const emit = defineEmits(["update"]);

const propsData = defineProps<Props>();
const radioValue = ref(2);
const weekday = ref(2);
const cycle01 = ref(1);
const cycle02 = ref(2);
const average01 = ref(1);
const average02 = ref(2);
const checkboxList = ref([]);
const weekList = ref<Week[]>([
  {
    key: 1,
    value: "星期一",
  },
  {
    key: 2,
    value: "星期二",
  },
  {
    key: 3,
    value: "星期三",
  },
  {
    key: 4,
    value: "星期四",
  },
  {
    key: 5,
    value: "星期五",
  },
  {
    key: 6,
    value: "星期六",
  },
  {
    key: 7,
    value: "星期日",
  },
]);
const checkNum = propsData.check;

defineExpose({
  cycle01,
  cycle02,
  average01,
  average02,
  checkboxList,
});

// 计算两个周期值
const cycleTotal = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  cycle01.value = checkNum(cycle01.value, 1, 7);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  cycle02.value = checkNum(cycle02.value, 1, 7);
  return cycle01.value + "-" + cycle02.value;
});

// 计算平均用到的值
const averageTotal = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average01.value = checkNum(average01.value, 1, 4);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average02.value = checkNum(average02.value, 1, 7);
  return average01.value + "#" + average02.value;
});
// 最近的工作日（格式）
const weekdayCheck = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  weekday.value = checkNum(weekday.value, 1, 7);
  return weekday.value;
});
// 计算勾选的checkbox值合集
const checkboxString = computed(() => {
  let str = checkboxList.value.join();
  return str == "" ? "*" : str;
});
watch(radioValue, (newVlue, oldValue) => {
  radioChange();
});
watch(cycleTotal, (newVlue, oldValue) => {
  cycleChange();
});
watch(averageTotal, (newVlue, oldValue) => {
  averageChange();
});
watch(checkboxString, (newVlue, oldValue) => {
  checkboxChange();
});
watch(weekdayCheck, (newVlue, oldValue) => {
  weekdayChange();
});
watch(propsData, (newVlue, oldValue) => {
  resoleCron(newVlue.cron.week);
});

//反解析Cron小时
function resoleCron(value?: string) {
  if (value) {
    if (value == "*") {
      radioValue.value = 1;
    } else if (value == "?") {
      radioValue.value = 2;
    } else if (typeof value === "string" && value.indexOf("-") > -1) {
      radioValue.value = 3;
    } else if (typeof value === "string" && value.indexOf("#") > -1) {
      radioValue.value = 4;
    } else if (typeof value === "string" && value.indexOf("L") > -1) {
      radioValue.value = 5;
    } else {
      radioValue.value = 6;
    }
  }
}
// 单选按钮值变化时
function radioChange() {
  // if (radioValue.value !== 2 && propsData.cron.day !== "?") {
  //   emit("update", "day", "?", "week");
  // }
  switch (radioValue.value) {
    case 1:
      emit("update", "week", "*");
      break;
    case 2:
      emit("update", "week", "?");
      break;
    case 3:
      emit("update", "week", cycleTotal.value);
      break;
    case 4:
      emit("update", "week", averageTotal.value);
      break;
    case 5:
      emit("update", "week", weekdayCheck.value + "L");
      break;
    case 6:
      emit("update", "week", checkboxString.value);
      break;
  }
}

// 周期两个值变化时
function cycleChange() {
  if (radioValue.value == 3) {
    emit("update", "week", cycleTotal.value);
  }
}
// 平均两个值变化时
function averageChange() {
  if (radioValue.value == 4) {
    emit("update", "week", averageTotal.value);
  }
}
// 最近工作日值变化时
function weekdayChange() {
  if (radioValue.value == 5) {
    emit("update", "week", weekday.value + "L");
  }
}
// checkbox值变化时
function checkboxChange() {
  if (radioValue.value == 6) {
    emit("update", "week", checkboxString.value);
  }
}
</script>
