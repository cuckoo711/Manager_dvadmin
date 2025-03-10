<template>
  <!-- 玩家信息 -->
  <el-form :model="player" label-width="auto" label-position="left">
    <el-divider content-position="left">
      <el-tag>玩家信息 (ID为空即为全服邮件)</el-tag>
    </el-divider>
    <el-form-item label="角色ID">
      <el-input v-model="player.roleId" placeholder="请输入角色ID" clearable @blur="getRoleInfo"/>
    </el-form-item>
    <el-form-item label="角色区服">
      <el-select v-model="player.region" placeholder="请选择区服" filterable @change="getRoleInfo">
        <el-option
            v-for="item in props.GDGameBaseInfo.data.Servers"
            :key="item.label"
            :label="item.label"
            :value="item.value"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="角色名">
      <el-input v-model="player.roleName" disabled v-loading="pinfoloading"/>
    </el-form-item>
    <el-form-item label="角色充值">
      <el-input v-model="player.charge" disabled v-loading="pinfoloading"/>
    </el-form-item>
  </el-form>
  <!-- 红颜信息 -->
  <el-form label-width="auto" label-position="left" :model="editvalue">
    <el-divider content-position="left">
      <el-tag>红颜信息</el-tag>
    </el-divider>
    <el-form-item label="所有红颜">
      <el-select v-model="editvalue.wifesall" placeholder="请选择红颜" filterable
                 style="width: calc(100% - 90px) !important; margin-right: 20px">
        <el-option
            v-for="item in wifes.wifesall"
            :key="item.value"
            :label="item.label"
            :value="item.value"
        />
      </el-select>
      <el-button type="primary" @click="addWife">添加</el-button>
    </el-form-item>
    <el-form-item label="已拥有">
      <el-select v-model="editvalue.wifeshave" placeholder="请选择红颜" filterable
                 style="width: calc(100% - 90px) !important; margin-right: 20px"
                 @change="getWifeInfo">
        <el-option
            v-for="item in wifes.wifeshave"
            :key="item.value"
            :label="item.label"
            :value="item.value"
        />
      </el-select>
      <el-button type="danger" @click="removeWife">删除</el-button>
    </el-form-item>
    <el-form-item label="红颜亲密">
      <el-tooltip v-if="!editvalue.wifeshave" content="请先选择已拥有红颜" placement="top">
        <el-input-number v-model="editvalue.intimacy" placeholder="请输入亲密度" clearable :min="0"
                         style="width: calc(100% - 90px) !important; margin-right: 20px" disabled/>
      </el-tooltip>
      <el-input-number
          v-else
          v-model="editvalue.intimacy"
          placeholder="请输入亲密度"
          clearable
          :min="0"
          style="width: calc(100% - 90px) !important; margin-right: 20px"
      />
      <el-button type="primary" @click="setIntimacy">设置</el-button>
      <p style="color: #aaaaaa;font-size:12px; height: 18px">
        原亲密：{{ wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.intimacy || 0 }}
        ({{
          numberToChineseReading((wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.intimacy || 0).toString())
        }})
      </p>
    </el-form-item>
    <el-form-item label="红颜魅力">
      <el-tooltip v-if="!editvalue.wifeshave" content="请先选择已拥有红颜" placement="top">
        <el-input-number v-model="editvalue.charm" placeholder="请输入魅力值" clearable :min="0"
                         style="width: calc(100% - 90px) !important; margin-right: 20px" disabled/>
      </el-tooltip>
      <el-input-number
          v-else
          v-model="editvalue.charm"
          placeholder="请输入魅力值"
          clearable
          :min="0"
          style="width: calc(100% - 90px) !important; margin-right: 20px"
      />
      <el-button type="primary" @click="setCharm">设置</el-button>
      <p style="color: #aaaaaa;font-size:12px; height: 18px">
        原魅力：{{ wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.charm || 0 }}
        ({{
          numberToChineseReading((wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.charm || 0).toString())
        }})
      </p>
    </el-form-item>
    <el-form-item label="红颜经验">
      <el-tooltip v-if="!editvalue.wifeshave" content="请先选择已拥有红颜" placement="top">
        <el-input-number v-model="editvalue.exp" placeholder="请输入经验值" clearable :min="0"
                         style="width: calc(100% - 90px) !important; margin-right: 20px" disabled/>
      </el-tooltip>
      <el-input-number
          v-else
          v-model="editvalue.exp"
          placeholder="请输入经验值"
          clearable
          :min="0"
          style="width: calc(100% - 90px) !important; margin-right: 20px"
      />
      <el-button type="primary" @click="setExp">设置</el-button>
      <p style="color: #aaaaaa;font-size:12px; height: 18px">
        原经验：{{ wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.exp || 0 }}
        ({{
          numberToChineseReading((wifes.wifeshave.find(item => item.value === editvalue.wifeshave)?.exp || 0).toString())
        }})
      </p>
    </el-form-item>
  </el-form>

  <!-- 操作按钮 -->
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="warning" @click="resetAll">清空输入</el-button>
  </el-button-group>

</template>

<script lang="ts" setup>
import {ref} from 'vue';
import {ElMessage} from 'element-plus';
import {GDGameBaseInfoStates} from '/@/views/gdbackend/GDFunction/gdgamebaseinfo';
import {AddWifes, DelWifes, EditWifes, GetRoleInfo, GetWifesList} from '/@/views/gdbackend/GDFunction/api';
import * as Nzh from 'nzh';

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

// function handleReload() {
//   emit('reload');
// }

const props = defineProps<{
  GDGameBaseInfo: GDGameBaseInfoStates;
}>();

interface editViewForm {
  wifeshave: string
  wifesall: string
  intimacy: number
  charm: number
  exp: number
}

const pinfoloading = ref(false);

const player = ref({
  roleId: '',
  region: '1001',
  roleName: '无效',
  charge: '无效',
});

interface Wife {
  label: string;
  value: string;
}

interface WifeHave {
  label: string;
  value: string;
  intimacy: string;
  charm: string;
  exp: string;
}

const wifes = ref<{
  wifesall: Wife[];
  wifeshave: WifeHave[];
}>({
  wifesall: [],
  wifeshave: [],
});


const editvalue = ref<editViewForm>({
  wifesall: '',
  wifeshave: '',
  intimacy: 0,
  charm: 0,
  exp: 0,
});


function getWifeInfo() {
  editvalue.value.intimacy = Number(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.intimacy || 0)
  editvalue.value.charm = Number(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.charm || 0)
  editvalue.value.exp = Number(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.exp || 0)
}

async function getRoleInfo() {
  resetAll(false); // 重置数据
  if (!player.value.roleId) {
    ElMessage.warning('请输入角色ID');
    return;
  }
  pinfoloading.value = true;
  try {
    const pinfo = await GetRoleInfo(props.GDGameBaseInfo.token, player.value.region, player.value.roleId);
    if (!pinfo || !pinfo.data || pinfo.data.roleName === '无效') {
      ElMessage.warning('无法获取玩家信息');
    }

    player.value.roleName = pinfo.data.roleName || '无效';
    player.value.charge = pinfo.data.charge || '无效';

    const wifesList = await GetWifesList(props.GDGameBaseInfo.token, player.value.region, player.value.roleName);
    wifes.value.wifesall = wifesList.data.wifesall;
    wifes.value.wifeshave = wifesList.data.wifeshave;

    handleLogger(`获取玩家信息成功: ${player.value.roleName} - ${player.value.charge}`, false);
  } catch (error: any) {
    ElMessage.error(error.message || '获取玩家信息失败');
    player.value.roleName = '无效';
    player.value.charge = '无效';
  } finally {
    pinfoloading.value = false;
  }
}


function resetAll(all: boolean = true) {
  if (all) {
    Object.assign(player.value, {
      roleId: '',
      region: '1001',
      roleName: '无效',
      charge: '无效',
    });
  } else {
    Object.assign(player.value, {
      roleName: '无效',
      charge: '无效',
    })
  }
  Object.assign(wifes.value, {
    wifesall: [],
    wifeshave: [],
  });
  Object.assign(editvalue.value, {
    wifesall: '',
    wifehave: '',
    intimacy: 0,
    charm: 0,
    exp: 0,
  });
  if (all) {
    ElMessage.success('已清空所有信息');
    handleLogger('已清空所有信息', false);
  }
}

async function setIntimacy() {
  if (!editvalue.value.intimacy) {
    ElMessage.warning('请输入亲密度');
    return;
  }
  if (!editvalue.value.wifeshave) {
    ElMessage.error('请选择要修改的红颜');
    return;
  }
  // 判断是否已经添加
  if (!(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave))) {
    ElMessage.error('该红颜未拥有');
    return;
  }
  await EditWifes(
      props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleName,
      editvalue.value.wifeshave,
      String(editvalue.value.intimacy),
      1
  ).then((res: boolean) => {
    if (res) {
      ElMessage.success('设置红颜亲密度成功');
      handleLogger(`设置用户[${player.value.roleName}(${player.value.roleId})]的红颜亲密度: ${editvalue.value.intimacy}
      (原亲密度${wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.intimacy})`);
      getRoleInfo();
    } else {
      ElMessage.error('设置红颜亲密度失败');
    }
  })
  handleLogger('设置红颜亲密度', false)
}

async function setCharm() {
  if (!editvalue.value.charm) {
    ElMessage.warning('请输入魅力值');
    return;
  }
  if (!editvalue.value.wifeshave) {
    ElMessage.error('请选择要修改的红颜');
    return;
  }
  // 判断是否已经添加
  if (!(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave))) {
    ElMessage.error('该红颜未拥有');
    return;
  }
  await EditWifes(
      props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleName,
      editvalue.value.wifeshave,
      String(editvalue.value.charm),
      2
  ).then((res: boolean) => {
    if (res) {
      ElMessage.success('设置红颜魅力成功');
      handleLogger(`设置用户[${player.value.roleName}(${player.value.roleId})]的红颜魅力: ${editvalue.value.charm}
      (原魅力${wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.charm})`);
      getRoleInfo();
    } else {
      ElMessage.error('设置红颜魅力失败');
    }
  })
}

async function setExp() {
  if (!editvalue.value.exp) {
    ElMessage.warning('请输入经验值');
    return;
  }
  if (!editvalue.value.wifeshave) {
    ElMessage.error('请选择要修改的红颜');
    return;
  }
  // 判断是否已经添加
  if (!(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave))) {
    ElMessage.error('该红颜未拥有');
    return;
  }
  await EditWifes(
      props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleName,
      editvalue.value.wifeshave,
      String(editvalue.value.exp),
      3
  ).then((res: boolean) => {
    if (res) {
      ElMessage.success('设置红颜经验成功');
      handleLogger(`设置用户[${player.value.roleName}(${player.value.roleId})]的红颜经验: ${editvalue.value.exp}
      (原经验${wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)?.exp})`);
      getRoleInfo();
    }
  })
}

async function addWife() {
  if (!editvalue.value.wifesall) {
    ElMessage.error('请选择要添加的红颜');
    return;
  }
  // 判断是否已经添加
  if (wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave)) {
    ElMessage.error('该红颜已拥有');
    return;
  }
  await AddWifes(props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleName,
      editvalue.value.wifesall
  ).then((res: boolean) => {
    if (res) {
      ElMessage.success('添加红颜 [' + editvalue.value.wifesall + '] 成功');
      handleLogger(`添加用户[${player.value.roleName}(${player.value.roleId})]的红颜: ${editvalue.value.wifesall}`);
      getRoleInfo();
      editvalue.value.wifesall = '';
    } else {
      ElMessage.error('添加红颜 [' + editvalue.value.wifesall + '] 失败');
    }
  })
}

async function removeWife() {
  if (!editvalue.value.wifeshave) {
    ElMessage.error('请选择要删除的红颜');
    return;
  }
  // 判断是否已经添加
  if (!(wifes.value.wifeshave.find(item => item.value === editvalue.value.wifeshave))) {
    ElMessage.error('该红颜未拥有');
    return;
  }
  await DelWifes(props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleName,
      editvalue.value.wifeshave
  ).then((res: boolean) => {
    if (res) {
      ElMessage.success('删除红颜 [' + editvalue.value.wifeshave + '] 成功');
      handleLogger(`删除用户[${player.value.roleName}(${player.value.roleId})]的红颜: ${editvalue.value.wifeshave}`);
      getRoleInfo();
      editvalue.value.wifeshave = '';
    } else {
      ElMessage.error('删除红颜 [' + editvalue.value.wifeshave + '] 失败');
    }
  })
}


function numberToChineseReading(numberString: string) {
  // 检查输入是否为自然数
  if (!/^-?\d+$/.test(numberString)) {
    return '非自然数';
  }
  return Nzh.cn.encodeS(numberString);
}

</script>
