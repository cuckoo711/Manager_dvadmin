<template>
  <el-form size="small">
    <el-form-item>
      <el-radio v-model="radioValue" :label="1">
        分钟，允许的通配符[, - * /]
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="2">
        周期从
        <el-input-number v-model="cycle01" :min="0" :max="58" />
        -
        <el-input-number
          v-model="cycle02"
          :min="cycle01 ? cycle01 + 1 : 1"
          :max="59"
        />
        分钟
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="3">
        从
        <el-input-number v-model="average01" :min="0" :max="58" />
        分钟开始，每
        <el-input-number
          v-model="average02"
          :min="1"
          :max="59 - average01 || 0"
        />
        分钟执行一次
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio v-model="radioValue" :label="4">
        指定
        <el-select
          clearable
          v-model="checkboxList"
          placeholder="可多选"
          multiple
          style="width: 100%"
        >
          <el-option v-for="item in 60" :key="item" :value="item - 1">
            {{ item - 1 }}
          </el-option>
        </el-select>
      </el-radio>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { defineExpose } from "vue";
import { CrontabValueObj } from "./cron";
import {ref,computed,watch} from 'vue';
//从父级接收数据，定义接口
interface Props {
  cron: CrontabValueObj;
  check: Function;
}

const emit = defineEmits(["update"]);

const propsData = defineProps<Props>();
const radioValue = ref(1);
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
  cycle01.value = checkNum(cycle01.value, 0, 58);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  cycle02.value = checkNum(
    cycle02.value,
    cycle01.value ? cycle01.value + 1 : 1,
    59
  );
  return cycle01.value + "-" + cycle02.value;
});

// 计算平均用到的值
const averageTotal = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average01.value = checkNum(average01.value, 0, 58);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average02.value = checkNum(average02.value, 1, 59 - average01.value || 0);
  return average01.value + "/" + average02.value;
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
watch(propsData, (newVlue, oldValue) => {
  resoleCron(newVlue.cron.min);
});

//反解析Cron分钟
function resoleCron(value?: string) {
  if (value) {
    if (value == "*") {
      radioValue.value = 1;
    } else if (typeof value === "string" && value.indexOf("-") > -1) {
      radioValue.value = 2;
    } else if (typeof value === "string" && value.indexOf("/") > -1) {
      radioValue.value = 3;
    } else {
      radioValue.value = 4;
    }
  }
}
// 单选按钮值变化时
function radioChange() {
  switch (radioValue.value) {
    case 1:
      emit("update", "min", "*", "min");
      break;
    case 2:
      emit("update", "min", cycleTotal.value, "min");
      break;
    case 3:
      emit("update", "min", averageTotal.value, "min");
      break;
    case 4:
      emit("update", "min", checkboxString.value, "min");
      break;
  }
}
// 周期两个值变化时
function cycleChange() {
  if (radioValue.value == 2) {
    emit("update", "min", cycleTotal.value, "min");
  }
}
// 平均两个值变化时
function averageChange() {
  if (radioValue.value == 3) {
    emit("update", "min", averageTotal.value, "min");
  }
}
// checkbox值变化时
function checkboxChange() {
  if (radioValue.value == 4) {
    emit("update", "min", checkboxString.value, "min");
  }
}
</script>
