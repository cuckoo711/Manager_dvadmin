<template>
	<fs-page>
		<div>
			<el-container>
				<el-card shadow="always" style="width: 100%">
					<template #header>创建服务器实例</template>
					<el-table :data="[{}]" style="width: 100%">
						<el-table-column label="镜像选择" align="center" header-align="center">
							<template #default="scope">
								<el-tooltip content="选择实例的镜像" placement="bottom">
									<el-select v-model="serverImage" placeholder="请选择" style="width: 100%">
										<el-option v-for="item in serverImageData" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-tooltip>
							</template>
						</el-table-column>
						<el-table-column label="服务器规格" align="center" header-align="center">
							<template #default="scope">
								<el-tooltip content="选择实例的规格" placement="bottom">
									<el-select v-model="serverSpec" placeholder="请选择" style="width: 100%">
										<el-option v-for="item in serverSpecData" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-tooltip>
							</template>
						</el-table-column>
						<el-table-column label="实例名称（游戏名）" align="center" header-align="center">
							<template #default="scope">
                <el-tooltip content="实例备注名，无实际意义，仅用做备注" placement="bottom">
								<el-input v-model="gameName" placeholder="请输入" style="width: 100%" @change="validateGameName()" />
                </el-tooltip>
							</template>
						</el-table-column>
						<el-table-column label="域名网络名" align="center" header-align="center">
							<template #default="scope">
                <el-tooltip content="实例的域名网络名，仅需填写英文部分，如：test01test" placement="bottom">
								<el-input v-model="subDomain" placeholder="请输入" style="width: 100%" @change="validateSubDomain()" />
                </el-tooltip>
							</template>
						</el-table-column>
						<el-table-column label="操作" align="center" header-align="center">
							<template #default="scope">
								<el-button-group>
									<el-button type="primary" @click="doAdd">添加</el-button>
									<el-button type="warning" @click="clear">清空</el-button>
								</el-button-group>
							</template>
						</el-table-column>
					</el-table>
				</el-card>
			</el-container>
		</div>
		<div :style="{ height: 'calc(100% - 200px)' }">
			<fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
		</div>
	</fs-page>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CreateInstances } from '/@/views/dailyreport/Consoles/api';
import * as api from '/@/views/dailyreport/Consoles/api';

const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions });
const serverImage = ref<string>('');
const serverImageData = [
	{ label: '官斗服务器环境', value: 'image-ycarodfhev7s11pm9fuv' },
	{ label: '大圣独立码服务器镜像', value: 'image-ycwawlvlmmfwswu7tn5g' },
	{ label: '真江湖干净服务器', value: 'image-ydhmduviy1hu0r7cywo6' },
	{ label: '大秦干净服务器', value: 'image-ycod600rqgklsnewqkld' },
	{ label: '宝可梦游戏服', value: 'image-ycn84w4qspm05kdrid57' },
	{ label: '大明系列游戏服镜像', value: 'image-ycn7skopvhdbkt9wtdem' },
	{ label: '大明游戏服环境', value: 'image-ycn57mqkjmklsm2as1lh' },
];
const serverSpecData = [
	{ label: '2c4g(优先选这个)', value: 'ecs.e-c1m2.large' },
  { label: '2c4g(上一个售罄就选这个)', value: 'ecs.c3al.large' },
	{ label: '2c8g(优先选这个)', value: 'ecs.e-c1m4.large' },
  { label: '2c8g(上一个售罄就选这个)', value: 'ecs.g3a.large' },
	{ label: '4c8g(优先选这个)', value: 'ecs.e-c1m2.xlarge' },
  { label: '4c8g(上一个售罄就选这个)', value: 'ecs.c3al.xlarge' },
	{ label: '4c16g(优先选这个)', value: 'ecs.e-c1m4.xlarge' },
  { label: '4c16g(上一个售罄就选这个)', value: 'ecs.g3a.xlarge' },
  { label: '8c16g(优先选这个)', value: 'ecs.e-c1m2.2xlarge' },
  { label: '8c16g(上一个售罄就选这个)', value: 'ecs.c3a.2xlarge' },
  { label: '8c32g(优先选这个)', value: 'ecs.e-c1m4.2xlarge' },
  { label: '8c32g(上一个售罄就选这个)', value: 'ecs.g3al.2xlarge' },
  { label: '8c64g(优先选这个)', value: 'ecs.r2a.2xlarge' },
  { label: '8c64g(上一个售罄就选这个)', value: 'ecs.r3al.2xlarge' },
];
const serverSpec = ref<string>('');
const gameName = ref<string>('');
const subDomain = ref<string>('');

// 验证 gameName 的合规性
function validateGameName() {
	let value = gameName.value;

	// 1. 以字母或中文开头
	if (!/^[a-zA-Z\u4e00-\u9fa5]/.test(value)) {
		value = value.replace(/^[^a-zA-Z\u4e00-\u9fa5]+/, '');
	}

	// 2. 只能包含中文、字母、数字、点“.”、空格、下划线“_”、中划线“-”、等号“=”、英文逗号“,”、中文逗号“，”和中文句号“。”
	value = value.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '');

	// 3. 长度限制在255个字符以内
	if (value.length > 255) {
		value = value.substring(0, 255);
	}

	gameName.value = value;
}

function validateSubDomain() {
	let value = subDomain.value;

	// 1. 允许使用字母、数字
	value = value.replace(/[^a-zA-Z0-9\-.]/g, '');

	// 2. 不能以中划线和点开头或结尾
	value = value.replace(/^[\-.]+/, '').replace(/[\-.]+$/, '');

	// 3. 不能连续使用中划线和点
	value = value.replace(/([\-.]){2,}/g, '$1');

	subDomain.value = value;
}

// 清空所有输入字段
function clear() {
	serverImage.value = '';
	serverSpec.value = '';
	gameName.value = '';
	subDomain.value = '';
}

// 添加服务器
async function doAdd() {
	// 再次进行合规检查
	validateGameName();
	validateSubDomain();

	if (!serverImage.value) {
		ElMessage.error('镜像选择');
		return;
	}
	if (!serverSpec.value) {
		ElMessage.error('服务器规格');
		return;
	}
	if (!gameName.value) {
		ElMessage.error('实例名称（游戏名）');
		return;
	}
	if (!subDomain.value) {
		ElMessage.error('域名网络名');
		return;
	}
	// 一次确认 本次将以某种格式展示所选的数据
	try {
		await ElMessageBox.confirm(
			`
      <div>
        本次操作将创建一个 <span style="color: red;">新的服务器实例</span>，请确认所选数据：<br><br>
        镜像选择：<span style="color: red;">${serverImage.value}</span><br>
        服务器规格：<span style="color: red;">${serverSpec.value}</span><br>
        实例名称（游戏名）：<span style="color: red;">${gameName.value}</span><br>
        域名网络名：<span style="color: red;">${subDomain.value}</span>
      </div>
    `,
			'请确认所选数据',
			{
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning',
				dangerouslyUseHTMLString: true,
			}
		);
	} catch (e) {
		ElMessage({
			type: 'info',
			message: '已取消添加',
		});
		return;
	}

	// 二次确认
	try {
		await ElMessageBox.confirm(
			`
      <div>
        当前操作 <span style="color: red;">一经提交将不可撤销</span>，请谨慎操作！<br><br>
        提交后将自动从 <span style="color: red;">信控账户内扣费</span><br>
        并自动添加 <span style="color: red;">域名解析记录</span>
      </div>
    `,
			'是否确认创建服务器实例？',
			{
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning',
				dangerouslyUseHTMLString: true,
			}
		);
	} catch (e) {
		ElMessage({
			type: 'info',
			message: '已取消添加',
		});
		return;
	}

	// 三次确认 "您确保您已知晓本次操作将创建一个新的服务器实例吗？该过程可能持续20秒，期间请勿重复操作"
	try {
		await ElMessageBox.confirm(
			`
      <div>
        您确保您已知晓本次操作将创建一个新的服务器实例吗？<br><br>
        该过程可能持续20秒，期间<span style="color: red;">请勿重复操作!!!</span><br>
      </div>
    `,
			'请确认所选数据',
			{
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning',
				dangerouslyUseHTMLString: true,
			}
		);
	} catch (e) {
		ElMessage({
			type: 'info',
			message: '已取消添加',
		});
		return;
	}

	const params = {
		serverImage: serverImage.value,
		serverSpec: serverSpec.value,
		gameName: gameName.value,
		subDomain: subDomain.value,
	};
	console.log(params);

	const res = await CreateInstances(params);
	if (res.status) {
		await api.ManualRefresh();
		ElMessage.success('添加成功: ' + res.message);
		await crudExpose.doRefresh();
	} else {
		ElMessage.error(res.message);
	}
}

// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>
