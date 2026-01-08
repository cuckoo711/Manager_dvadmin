<template>
  <!-- 玩家信息 -->
  <el-divider content-position="left">
    <el-tag>玩家信息 (ID为空即为全服邮件)</el-tag>
  </el-divider>
  <el-form :model="player" label-width="auto" label-position="left">

    <el-form-item label="角色ID">
      <el-input v-model="player.roleId" placeholder="请输入角色ID" clearable @blur="getRoleInfo"
      ></el-input>
    </el-form-item>
    <el-form-item label="角色区服">
      <el-select v-model="player.region" placeholder="请选择区服" filterable @change="getRoleInfo">
        <el-option v-for="item in props.GDGameBaseInfo.data.Servers"
                   :key="item.label"
                   :label="item.label"
                   :value="item.value"/>
      </el-select>
    </el-form-item>
    <el-form-item label="角色名">
      <el-input v-model="player.roleName" placeholder="请输入角色名" disabled v-loading="pinfoloading"/>
    </el-form-item>
    <el-form-item label="角色充值">
      <el-input v-model="player.charge" placeholder="请输入充值金额" disabled v-loading="pinfoloading"/>
    </el-form-item>
  </el-form>

  <!-- 礼包信息 -->
  <el-divider content-position="left">
    <el-tag>礼包信息</el-tag>
  </el-divider>
  <el-form :model="gift" label-width="auto" label-position="left">
    <el-form-item label="邮件标题">
      <el-input v-model="gift.mailTitle" placeholder="请输入邮件标题"/>
    </el-form-item>
    <el-form-item label="邮件内容">
      <el-tooltip content="可手动输入自定义邮件内容" placement="top">
        <el-select v-model="gift.mailContent" placeholder="请选择邮件内容" allow-create default-first-option filterable>
          <el-option label="返利活动" value="返利活动"/>
          <el-option label="周常活动" value="周常活动"/>
          <el-option label="周末活动" value="周末活动"/>
          <el-option label="转游" value="转游"/>
        </el-select>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="礼包选择">
      <el-select v-model="gift.giftOption" placeholder="请选择礼包" filterable>
        <el-option v-for="item in props.GDGameBaseInfo.data.Gifts"
                   :key="item.label"
                   :label="item.label"
                   :value="item.value"/>
      </el-select>
    </el-form-item>
  </el-form>

  <!-- 操作按钮 -->
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="danger" @click="removeGift">删除礼包</el-button>
    <el-button type="primary" @click="showSendlogsVisible = true">发放记录</el-button>
    <el-button type="warning" @click="reSet">清空输入</el-button>
    <el-button type="success" @click="send">发放邮件</el-button>
  </el-button-group>
  <el-drawer v-model="showSendlogsVisible" title="邮件发放日志" size="80%" class="rounded-lg" destroy-on-close>
    <SendLogs :GDGameBaseInfo="props.GDGameBaseInfo"/>
  </el-drawer>
</template>

<script lang="ts" setup>
import {defineAsyncComponent, ref} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";
import {DelGifts, GetRoleInfo, SendGifts} from "/@/views/gdbackend/GDFunction/api";

const emit = defineEmits(['reload', 'logger']);

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

function handleReload() {
  emit('reload');
}

const props = defineProps<{
  GDGameBaseInfo: GDGameBaseInfoStates;
}>()

const SendLogs = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/SendLogs/index.vue'));
const showSendlogsVisible = ref(false)
const pinfoloading = ref(false)

const player = ref({
  roleId: '',
  region: '1001',
  roleName: '***群发***',
  charge: '***群发***'
});

const gift = ref({
  mailTitle: '',
  mailContent: '返利活动',
  giftOption: ''
});

async function getRoleInfo() {
  pinfoloading.value = true;
  if (!player.value.roleId) {
    player.value.roleName = '***群发***';
    player.value.charge = '***群发***';
    pinfoloading.value = false;
    return;
  }
  const pinfo = await GetRoleInfo(
      props.GDGameBaseInfo.token,
      player.value.region,
      player.value.roleId,
  )
  player.value.roleName = pinfo.data.roleName;
  player.value.charge = pinfo.data.charge;
  pinfoloading.value = false;
  handleLogger(`获取玩家信息成功: ${player.value.roleName} - ${player.value.charge}`, false);
}

async function removeGift() {
  if (!gift.value.giftOption) {
    ElMessage.error('请选择礼包');
    return;
  }
  const res = await DelGifts(
      props.GDGameBaseInfo.token,
      [gift.value.giftOption],
  );
  if (res.data === true) {
    ElMessage.success('删除成功');
  } else {
    ElMessage.error('删除失败');
  }
  handleLogger(`删除礼包成功: ${gift.value.giftOption}`);
  gift.value.giftOption = '';
  handleReload();
}

function reSet() {
  player.value = {
    roleId: '',
    region: '1001',
    roleName: '***群发***',
    charge: '***群发***'
  };
  gift.value = {
    mailTitle: '',
    mailContent: '返利活动',
    giftOption: ''
  };
  ElMessage.success('已清空所有信息');
  handleLogger('已清空所有信息', false);
}

async function send() {
  // 检查是否有未填写的信息
  if (!gift.value.mailTitle) {
    ElMessage.error('请填写邮件标题');
    return;
  }
  if (!gift.value.mailContent) {
    ElMessage.error('请选择邮件内容');
    return;
  }
  if (!gift.value.giftOption) {
    ElMessage.error('请选择礼包');
    return;
  }
  if (!player.value.roleId) {
    // 提示如果为空则为全服邮件，二次确认
    await ElMessageBox.confirm('玩家ID为空，是否确认为全服邮件？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).catch(() => {
      ElMessage.info('已取消');
      return;
    });
  } else {
    // 玩家ID不为空，检查是否无效
    if (player.value.roleName === '无效' || player.value.charge === '无效') {
      ElMessage.error('玩家信息无效，请检查');
      return;
    }
    await ElMessageBox.confirm('是否确认发放？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      await SendGifts(
          props.GDGameBaseInfo.token,
          player.value.region,
          gift.value.mailTitle,
          player.value.roleId,
          gift.value.giftOption,
          gift.value.mailContent,
      ).then((res) => {
        if (res.data === false) {
          ElMessage.error('发放失败');
        } else {
          ElMessage.success('发放成功');
          handleLogger(`发放成功: ${player.value.roleName}(${player.value.roleId}) - ${gift.value.mailTitle}[${props.GDGameBaseInfo.data.Gifts.find((item) => item.value === gift.value.giftOption)?.label}(${gift.value.giftOption})]`);
        }
      });
    }).catch(() => {
      ElMessage.info('已取消');
      return;
    });
  }

}

</script>
