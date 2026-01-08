<template>
  <el-form size="small">
    <el-form-item>
      <el-radio :label="1" v-model="radioValue">
        不填，允许的通配符[, - * /]
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio :label="2" v-model="radioValue">每年</el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio :label="3" v-model="radioValue">
        周期从
        <el-input-number v-model="cycle01" :min="fullYear" :max="2098" />
        -
        <el-input-number
          v-model="cycle02"
          :min="cycle01 ? cycle01 + 1 : fullYear + 1"
          :max="2099"
        />
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio :label="4" v-model="radioValue">
        从
        <el-input-number v-model="average01" :min="fullYear" :max="2098" />
        年开始，每
        <el-input-number
          v-model="average02"
          :min="1"
          :max="2099 - average01 || fullYear"
        />
        年执行一次
      </el-radio>
    </el-form-item>

    <el-form-item>
      <el-radio :label="5" v-model="radioValue">
        指定
        <el-select
          clearable
          v-model="checkboxList"
          placeholder="可多选"
          multiple
        >
          <el-option
            v-for="item in 9"
            :key="item"
            :value="item - 1 + fullYear"
            :label="item - 1 + fullYear"
          />
        </el-select>
      </el-radio>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { defineExpose } from "vue";
import { CrontabValueObj, Week } from "./cron";
import {ref,watch,computed,onMounted} from 'vue';
//从父级接收数据，定义接口
interface Props {
  cron: CrontabValueObj;
  check: Function;
}

const emit = defineEmits(["update"]);

const propsData = defineProps<Props>();
const radioValue = ref(1);
const fullYear = ref(0);
const cycle01 = ref(0);
const cycle02 = ref(0);
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
  cycle01.value = checkNum(cycle01.value, fullYear.value, 2098);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  cycle02.value = checkNum(
    cycle02.value,
    cycle01.value ? cycle01.value + 1 : fullYear.value + 1,
    2099
  );
  return cycle01.value + "-" + cycle02.value;
});

// 计算平均用到的值
const averageTotal = computed(() => {
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average01.value = checkNum(average01.value, fullYear.value, 2098);
  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  average02.value = checkNum(
    average02.value,
    1,
    2099 - average01.value || fullYear.value
  );
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
  resoleCron(newVlue.cron.year);
});

//反解析Cron小时
function resoleCron(value?: string) {
  if (value) {
    if (value == "") {
      radioValue.value = 1;
    } else if (value == "*") {
      radioValue.value = 2;
    } else if (typeof value === "string" && value.indexOf("-") > -1) {
      radioValue.value = 3;
    } else if (typeof value === "string" && value.indexOf("/") > -1) {
      radioValue.value = 4;
    } else {
      radioValue.value = 5;
    }
  }
}
onMounted(() => {
  // 仅获取当前年份
  fullYear.value = Number(new Date().getFullYear());
  cycle01.value = fullYear.value;
  cycle02.value = cycle01.value + 1;
  average01.value = fullYear.value;
});

function radioChange() {
  switch (radioValue.value) {
    case 1:
      emit("update", "year", "", "cronyear");
      break;
    case 2:
      emit("update", "year", "*", "cronyear");
      break;
    case 3:
      emit("update", "year", cycleTotal.value, "cronyear");
      break;
    case 4:
      emit("update", "year", averageTotal.value, "cronyear");
      break;
    case 5:
      emit("update", "year", checkboxString.value, "cronyear");
      break;
  }
}
// 周期两个值变化时
function cycleChange() {
  if (radioValue.value == 3) {
    emit("update", "year", cycleTotal.value, "cronyear");
  }
}
// 平均两个值变化时
function averageChange() {
  if (radioValue.value == 4) {
    emit("update", "year", averageTotal.value, "cronyear");
  }
}
// checkbox值变化时
function checkboxChange() {
  if (radioValue.value == 5) {
    emit("update", "year", checkboxString.value, "cronyear");
  }
}
</script>
