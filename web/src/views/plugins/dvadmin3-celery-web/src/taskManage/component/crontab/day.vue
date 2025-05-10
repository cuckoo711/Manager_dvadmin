<template>
  <el-form size="small">
    <el-form-item>
      <el-radio v-model="radioValue" :label="1">
        日，允许的通配符[, - * ? / L W]
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="2">不指定</el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="3">
        周期从
        <el-input-number v-model="cycle01" :min="1" :max="30" />
        -
        <el-input-number
          v-model="cycle02"
          :min="cycle01 ? cycle01 + 1 : 2"
          :max="31"
        />
        日
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="4">
        从
        <el-input-number v-model="average01" :min="1" :max="30" />
        号开始，每
        <el-input-number
          v-model="average02"
          :min="1"
          :max="31 - average01 || 1"
        />
        日执行一次
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="5">
        每月
        <el-input-number v-model="workday" :min="1" :max="31" />
        号最近的那个工作日
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="6">本月最后一天</el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="7">
        指定
        <el-select
          clearable
          v-model="checkboxList"
          placeholder="可多选"
          multiple
          style="width: 100%"
        >
          <el-option v-for="item in 31" :key="item" :value="item">
            {{ item }}
          </el-option>
        </el-select>
      </el-radio>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { defineExpose } from "vue";
import { CrontabValueObj } from "./cron";
import {ref,watch,computed} from 'vue';
//从父级接收数据，定义接口
interface Props {
  cron: CrontabValueObj;
  check: Function;
}

const emit = defineEmits(["update"]);

const propsData = defineProps<Props>();
const radioValue = ref(1);
const workday = ref(1);
const cycle01 = ref(1);
const cycle02 = ref(2);
const average01 = ref(0);
const average02 = ref(1);
const checkboxList = ref([]);
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
  cycle01.value = checkNum(cycle01.value, 0, 30);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  cycle02.value = checkNum(
    cycle02.value,
    cycle01.value ? cycle01.value + 1 : 2,
    31,
    31
  );
  return cycle01.value + "-" + cycle02.value;
});

// 计算平均用到的值
const averageTotal = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average01.value = checkNum(average01.value, 0, 30);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average02.value = checkNum(average02.value, 1, 31 - average01.value || 0);
  return average01.value + "/" + average02.value;
});
// 计算工作日格式
const workdayCheck = computed(() => {
  const _workday = checkNum(workday.value, 1, 31);
  return workday;
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
watch(workdayCheck, (newVlue, oldValue) => {
  workdayChange();
});
watch(propsData, (newVlue, oldValue) => {
  resoleCron(newVlue.cron.day);
});

//反解析Cron小时
function resoleCron(value?: string) {
  if (value) {
    if (value == "*") {
      radioValue.value = 1;
    } else if (value === "?") {
      radioValue.value = 2;
    } else if (typeof value === "string" && value.indexOf("-") > -1) {
      radioValue.value = 3;
    } else if (typeof value === "string" && value.indexOf("/") > -1) {
      radioValue.value = 4;
    } else if (typeof value === "string" && value.indexOf("W") > -1) {
      radioValue.value = 5;
    } else if (typeof value === "string" && value.indexOf("L") > -1) {
      radioValue.value = 6;
    } else {
      radioValue.value = 7;
    }
  }
}
// 单选按钮值变化时
function radioChange() {
  ("day rachange");

  switch (radioValue.value) {
    case 1:
      emit("update", "day", "*");
      break;
    case 2:
      emit("update", "day", "?");
      break;
    case 3:
      emit("update", "day", cycleTotal.value);
      break;
    case 4:
      emit("update", "day", averageTotal.value);
      break;
    case 5:
      emit("update", "day", workday.value + "W");
      break;
    case 6:
      emit("update", "day", "L");
      break;
    case 7:
      emit("update", "day", checkboxString.value);
      break;
  }
  ("day rachange end");
}
// 周期两个值变化时
function cycleChange() {
  if (radioValue.value == 3) {
    emit("update", "day", cycleTotal.value);
  }
}
// 平均两个值变化时
function averageChange() {
  if (radioValue.value == 4) {
    emit("update", "day", averageTotal.value);
  }
}
// 最近工作日值变化时
function workdayChange() {
  if (radioValue.value == 5) {
    emit("update", "day", workdayCheck.value + "W");
  }
}
// checkbox值变化时
function checkboxChange() {
  if (radioValue.value == 7) {
    emit("update", "day", checkboxString.value);
  }
}
</script>
