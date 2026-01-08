<template>
	<div class="popup-result">
		<p class="title">最近20次运行时间：{{ humanizeCronInChinese(propsData.expression) }}</p>
		<ul class="popup-result-scroll">
			<template v-if="isShow">
				<li v-for="item in resultList" :key="item">{{ item }}</li>
			</template>

			<li v-else>计算结果中...</li>
		</ul>
	</div>
</template>

<script setup lang="ts">
import { CrontabValueObj } from './cron';
import cronParser from 'cron-parser'; // 使用 ESModules 的方式导入
import { ref, watch, onMounted } from 'vue';
import { humanizeCronInChinese } from 'cron-chinese';

//从父级接收数据，定义接口
interface Props {
	expression: string;
}

const propsData = defineProps<Props>();
const dayRule = ref('');
const dayRuleSup = ref('');
const dateArr = ref<number[][]>([[]]);
const resultList = ref<string[]>([]);
const isShow = ref(false);
const curexpression = ref(propsData.expression);
watch(
	propsData,
	(newValue, oldValue) => {
		console.log('监控表达式：' + newValue.expression + '-' + oldValue?.expression);
		expressionChange(newValue.expression);
	},
	{ deep: true, immediate: true }
);
onMounted(() => {
	expressionChange(propsData.expression);
});

// 表达式值变化时，开始去计算结果
function expressionChange(expression: string) {
	// 解析 Cron 表达式
	let resultArr: any[] = [];
	try {
		const interval = cronParser.parseExpression(expression);
		const dates = [];

		// 计算接下来的 20 次运行时间
		for (let i = 0; i < 20; i++) {
			const date = interval.next(); // 获取下一个运行时间
			// 获取原始日期
			const originalDate = date.toDate();
			// 创建新的日期，加上 8 个小时
			originalDate.setHours(originalDate.getHours() + 8);
			// 格式化到分钟级别
			const formattedDate = originalDate.toISOString().slice(0, 16).replace('T', ' ');
			dates.push(formattedDate);
		}

		// 更新 Vue 数据
		resultArr = dates;
	} catch (err) {
		console.error('无效的 Cron 表达式:', err.message);
	}
	// 判断100年内的结果条数
	if (resultArr.length == 0) {
		resultList.value = ['没有达到条件的结果！'];
	} else {
		resultList.value = resultArr;
	}
	// 计算完成-显示结果
	isShow.value = true;
}

// 根据传进来的min-max返回一个顺序的数组
function getOrderArr(min: number, max: number) {
	let arr = [];
	for (let i = min; i <= max; i++) {
		arr.push(i);
	}
	return arr;
}

// 根据规则中指定的零散值返回一个数组
function getAssignArr(rule: string) {
	let arr = [];
	let assiginArr = rule.split(',');
	for (let i = 0; i < assiginArr.length; i++) {
		arr[i] = Number(assiginArr[i]);
	}
	arr.sort(compare);
	return arr;
}

// 根据一定算术规则计算返回一个数组
function getAverageArr(rule: string, limit: number) {
	let arr = [];
	let agArr = rule.split('/');
	let min = Number(agArr[0]);
	let step = Number(agArr[1]);
	while (min <= limit) {
		arr.push(min);
		min += step;
	}
	return arr;
}

// 根据规则返回一个具有周期性的数组
function getCycleArr(rule: string, limit: number, status: boolean) {
	// status--表示是否从0开始（则从1开始）
	let arr = [];
	let cycleArr = rule.split('-');
	let min = Number(cycleArr[0]);
	let max = Number(cycleArr[1]);
	if (min > max) {
		max += limit;
	}
	for (let i = min; i <= max; i++) {
		let add = 0;
		if (status === false && i % limit == 0) {
			add = limit;
		}
		arr.push(Math.round((i % limit) + add));
	}
	arr.sort(compare);
	return arr;
}

// 比较数字大小（用于Array.sort）
function compare(value1: number, value2: number) {
	if (value2 - value1 > 0) {
		return -1;
	} else {
		return 1;
	}
}

// 格式化日期格式如：2017-9-19 18:04:33
function formatDate(value: Date, type?: string) {
	// 计算日期相关值
	let time = typeof value == 'number' ? new Date(value) : value;
	let Y = time.getFullYear();
	let M = time.getMonth() + 1;
	let D = time.getDate();
	let h = time.getHours();
	let m = time.getMinutes();
	let s = time.getSeconds();
	let week = time.getDay();
	// 如果传递了type的话
	if (type == undefined) {
		return (
			Y +
			'-' +
			(M < 10 ? '0' + M : M) +
			'-' +
			(D < 10 ? '0' + D : D) +
			' ' +
			(h < 10 ? '0' + h : h) +
			':' +
			(m < 10 ? '0' + m : m) +
			':' +
			(s < 10 ? '0' + s : s)
		);
	} else if (type == 'week') {
		// 在quartz中 1为星期日
		return week + 1;
	}
}

// 格式化日期格式如：2017-9-19 18:04:33
function getWeek(value: Date) {
	// 计算日期相关值
	let time = typeof value == 'number' ? new Date(value) : value;
	let Y = time.getFullYear();
	let M = time.getMonth() + 1;
	let D = time.getDate();
	let h = time.getHours();
	let m = time.getMinutes();
	let s = time.getSeconds();
	let week = time.getDay();

	// 在quartz中 1为星期日
	return week + 1;
}

// 检查日期是否存在
function checkDate(value: string) {
	let time = new Date(value);
	let format = formatDate(time);
	return value === format;
}
</script>
<style lang="scss" scoped>

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
