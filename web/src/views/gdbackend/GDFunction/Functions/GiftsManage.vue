<template>
  <el-form label-width="auto" label-position="left">
    <el-divider content-position="left">
      <el-tag>添加礼包</el-tag>
    </el-divider>
    <el-form-item label="礼包名称">
      <el-input v-model="gift.giftName" placeholder="请输入礼包名称" clearable/>
    </el-form-item>
    <el-form-item label="礼包描述">
      <el-input
          type="textarea"
          v-model="gift.giftDesc"
          placeholder="请输入礼包描述"
          :autosize="{ minRows: 2, maxRows: 4 }"
          style="width: calc(100% - 150px) !important; margin-right: 20px"
      />
      <el-tooltip content="匹配礼包" placement="top">
        <el-button :icon="MagicStick" @click="MatchGiftsDesc" type="text">
          匹配
        </el-button>
      </el-tooltip>
      <el-tooltip content="重载礼包" placement="top">
        <el-button :icon="RefreshRight" @click="MatchRefresh" type="text">
          重载
        </el-button>
      </el-tooltip>
    </el-form-item>

    <el-form-item label="道具名称">
      <el-tooltip :content="selectedGiftLabel" placement="top-start" effect="dark" :disabled="!giftSelect">
        <el-select v-model="giftSelect" placeholder="请选择道具" filterable @change="MatchGiftsCount">
          <el-option
              v-for="item in giftOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </el-tooltip>
    </el-form-item>

    <el-form-item label="道具数量">
      <el-input-number
          v-model="giftCount"
          :min="0"
          step-strictly
          style="width: calc(100% - 100px) !important; margin-right: 20px"
      >
        <template #decrease-icon>
          <el-icon>
            <ArrowDown/>
          </el-icon>
        </template>
        <template #increase-icon>
          <el-icon>
            <ArrowUp/>
          </el-icon>
        </template>
      </el-input-number>
      <el-tooltip content="添加(将数值累加)" placement="top">
        <el-button :icon="CirclePlusFilled" @click="AddToProps" type="text">
          添加
        </el-button>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="充值货币">
      <el-input-number
          v-model="giftSPcount.gold"
          :min="0"
          step-strictly
          style="width: calc(100% - 100px) !important; margin-right: 20px"
      >
        <template #decrease-icon>
          <el-icon>
            <ArrowDown/>
          </el-icon>
        </template>
        <template #increase-icon>
          <el-icon>
            <ArrowUp/>
          </el-icon>
        </template>
      </el-input-number>
      <el-tooltip content="添加(直接设置数值)" placement="top">
        <el-button :icon="CirclePlusFilled" @click="AddGOLDToProps" type="text">
          添加
        </el-button>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="普通货币">
      <el-input-number
          v-model="giftSPcount.money"
          :min="0"
          step-strictly
          style="width: calc(100% - 100px) !important; margin-right: 20px"
      >
        <template #decrease-icon>
          <el-icon>
            <ArrowDown/>
          </el-icon>
        </template>
        <template #increase-icon>
          <el-icon>
            <ArrowUp/>
          </el-icon>
        </template>
      </el-input-number>
      <el-tooltip content="添加(直接设置数值)" placement="top">
        <el-button :icon="CirclePlusFilled" @click="AddMONEYToProps" type="text">
          添加
        </el-button>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="政绩">
      <el-input-number
          v-model="giftSPcount.government"
          :min="0"
          step-strictly
          style="width: calc(100% - 100px) !important; margin-right: 20px"
      >
        <template #decrease-icon>
          <el-icon>
            <ArrowDown/>
          </el-icon>
        </template>
        <template #increase-icon>
          <el-icon>
            <ArrowUp/>
          </el-icon>
        </template>
      </el-input-number>
      <el-tooltip content="添加(直接设置数值)" placement="top">
        <el-button :icon="CirclePlusFilled" @click="AddGOVToProps" type="text">
          添加
        </el-button>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="VIP经验">
      <el-input-number
          v-model="giftSPcount.vipExp"
          :min="0"
          step-strictly
          style="width: calc(100% - 100px) !important; margin-right: 20px"
      >
        <template #decrease-icon>
          <el-icon>
            <ArrowDown/>
          </el-icon>
        </template>
        <template #increase-icon>
          <el-icon>
            <ArrowUp/>
          </el-icon>
        </template>
      </el-input-number>
      <el-tooltip content="添加(直接设置数值)" placement="top">
        <el-button :icon="CirclePlusFilled" @click="AddVIPExpToProps" type="text">
          添加
        </el-button>
      </el-tooltip>
    </el-form-item>
    <el-form-item label="道具代码">
      <el-input
          type="textarea"
          v-model="gift.giftContent"
          placeholder="请添加道具或手动输入道具代码"
          :autosize="{ minRows: 2, maxRows: 4 }"
          style="width: calc(100%) !important"
      />
    </el-form-item>
  </el-form>
  <el-divider content-position="left">
    <el-tag>操作</el-tag>
  </el-divider>
  <el-button-group>
    <el-button type="primary" @click="showGiftsListVisible = true">礼包列表</el-button>
    <el-button type="warning" @click="reSet">清空输入</el-button>
    <el-button type="success" @click="handleUpload">上传礼包</el-button>
  </el-button-group>
  <el-drawer v-model="showGiftsListVisible" title="礼包列表" size="80%" class="rounded-lg" destroy-on-close>
    <GiftsList :GDGameBaseInfo="props.GDGameBaseInfo"/>
  </el-drawer>

</template>

<script lang="ts" setup>
import {computed, defineAsyncComponent, ref, watch} from 'vue';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";
import {ArrowDown, ArrowUp, CirclePlusFilled, MagicStick, RefreshRight} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox} from "element-plus";
import {AddGifts} from "/@/views/gdbackend/GDFunction/api";

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

const GiftsList = defineAsyncComponent(() => import('/@/views/gdbackend/GDFunction/Functions/GiftsList/index.vue'));
const showGiftsListVisible = ref(false)
const gift = ref({
  giftName: '',
  giftDesc: '',
  giftContent: '',
})
const giftSPcount = ref({
  gold: 0,
  money: 0,
  government: 0,
  vipExp: 0,
})

const giftOptions = ref<{ label: string; value: string; }[]>([])
const giftSelect = ref('')
const giftCount = ref(0)

function MatchGiftsDesc() {
  if (!gift.value.giftDesc) {
    ElMessage.warning('请先输入礼包描述');
    return;
  }

  giftSelect.value = '';
  const giftDesc = gift.value.giftDesc;
  const sids = props.GDGameBaseInfo.data.Sids.map((item: { label: string; value: string }) => item.label);

  let temp: string[];
  temp = sids.filter((key: string) => giftDesc.includes(key));
  const setMatch = giftDesc.match(/(..).件套/);
  if (setMatch) {
    temp = temp.concat(sids.filter((key: string) => key.includes(setMatch[1])));
  }
  const suitMatch = giftDesc.match(/(..)套装/);
  if (suitMatch) {
    temp = temp.concat(sids.filter((key: string) => key.includes(suitMatch[1])));
  }
  if (temp.length === 0) {
    handleLogger('未匹配到道具', false);
    ElMessage.warning('未匹配到道具');
    MatchRefresh();
    return;
  }
  handleLogger('匹配结果:' + temp, false);
  ElMessage.success('匹配成功, 共匹配到' + temp.length + '个道具');
  giftOptions.value = props.GDGameBaseInfo.data.Sids.filter((item: {
    label: string;
    value: string
  }) => temp.includes(item.label));
}

function MatchGiftsCount() {
  if (!giftSelect.value) {
    ElMessage.warning('请先选择道具');
    return;
  }
  const giftDesc = gift.value.giftDesc;
  const giftSelectLabel = giftOptions.value.find((item: {
    label: string;
    value: string;
  }) => item.value === giftSelect.value)?.label;
  if (!giftSelectLabel) {
    ElMessage.warning('未找到对应道具');
    return;
  }
  const cmCount = giftDesc.match(new RegExp(`${giftSelectLabel}.*?([0-9]+)`));
  if (cmCount) {
    giftCount.value = parseInt(cmCount[1]);
  } else {
    const allMatches = [...giftDesc.matchAll(/([\u4e00-\u9fa5]+)\*([0-9]+)/g)];
    for (const match of allMatches) {
      const cmName = match[1].replace(/.件套|套装/, '');
      if (giftSelectLabel.includes(cmName) || cmName.includes(giftSelectLabel)) {
        giftCount.value = parseInt(match[2]);
        return;
      }
    }
  }
}

function reSet(name: boolean = true) {
  if (name) {
    gift.value.giftName = '';
  }
  gift.value.giftDesc = '';
  gift.value.giftContent = '';
  giftSPcount.value = {
    gold: 0,
    money: 0,
    government: 0,
    vipExp: 0,
  };
  giftSelect.value = '';
  giftCount.value = 0;
  giftOptions.value = props.GDGameBaseInfo.data.Sids;
  ElMessage.success('已清空所有信息');
  handleLogger('已清空所有信息', false);
}

function MatchRefresh() {
  giftOptions.value = props.GDGameBaseInfo.data.Sids
}

function AddGOLDToProps() {
  if (giftSPcount.value.gold <= 0) {
    ElMessage.error('货币数量不能为零');
    return;
  }
  const newGiftContent = `gold:${giftSPcount.value.gold};`;
  const typeRegex = new RegExp('(gold:.*?;)');
  const existingContent = gift.value.giftContent;
  const match = existingContent.match(typeRegex);
  if (match) {
    gift.value.giftContent = existingContent.replace(match[0], newGiftContent);
  } else {
    gift.value.giftContent += newGiftContent;
  }
}

function AddMONEYToProps() {
  if (giftSPcount.value.money <= 0) {
    ElMessage.error('货币数量不能为零');
    return;
  }
  const newGiftContent = `money:${giftSPcount.value.money};`;
  const typeRegex = new RegExp('(money:.*?;)');
  const existingContent = gift.value.giftContent;
  const match = existingContent.match(typeRegex);
  if (match) {
    gift.value.giftContent = existingContent.replace(match[0], newGiftContent);
  } else {
    gift.value.giftContent += newGiftContent;
  }
}

function AddGOVToProps() {
  if (giftSPcount.value.government <= 0) {
    ElMessage.error('政绩数量不能为零');
    return;
  }
  const newGiftContent = `government:${giftSPcount.value.government};`;
  const typeRegex = new RegExp('(government:.*?;)');
  const existingContent = gift.value.giftContent;
  const match = existingContent.match(typeRegex);
  if (match) {
    gift.value.giftContent = existingContent.replace(match[0], newGiftContent);
  } else {
    gift.value.giftContent += newGiftContent;
  }
}

function AddVIPExpToProps() {
  if (giftSPcount.value.vipExp <= 0) {
    ElMessage.error('VIP经验数量不能为零');
    return;
  }
  const newGiftContent = `vipExp:${giftSPcount.value.vipExp};`;
  const typeRegex = new RegExp('(vipExp:.*?;)');
  const existingContent = gift.value.giftContent;
  const match = existingContent.match(typeRegex);
  if (match) {
    gift.value.giftContent = existingContent.replace(match[0], newGiftContent);
  } else {
    gift.value.giftContent += newGiftContent;
  }
}

function AddToProps() {
  if (!giftSelect.value) {
    ElMessage.warning('请先选择道具');
    return;
  }
  if (giftCount.value <= 0) {
    ElMessage.error('道具数量不能为零');
    return;
  }
  if (!giftSelect.value) {
    ElMessage.warning('未找到选中的道具');
    return;
  }

  // 生成道具代码
  const newGiftContent = `${giftSelect.value}:${giftCount.value}`;

  // 确定道具类型
  let typeKey = '';
  for (const [key, items] of Object.entries(props.GDGameBaseInfo.data.SidsDict)) {
    if (items.some(item => item.value === giftSelect.value)) {
      typeKey = key;
      break;
    }
  }
  if (!typeKey) {
    ElMessage.warning('未找到对应的道具类型');
    return;
  }

  // 查找是否已经存在该类型的道具信息
  const typeRegex = new RegExp(`(${typeKey}:.*?;)`);
  const existingContent = gift.value.giftContent;
  const match = existingContent.match(typeRegex);

  if (match) {
    // 如果存在该道具类型，进一步查找是否包含相同道具的数量信息
    const dataRegex = new RegExp(`(${giftSelect.value}):([0-9]*)`);
    const dataMatch = existingContent.match(dataRegex);

    if (dataMatch) {
      // 如果已存在相同道具，更新数量(覆盖)
      gift.value.giftContent = existingContent.replace(dataMatch[0], `${giftSelect.value}:${giftCount.value}`);
    } else {
      // 如果没有相同道具，添加新的道具信息
      const updatedContent = match[0].replace(';', `:${newGiftContent};`);
      gift.value.giftContent = existingContent.replace(match[0], updatedContent);
    }
  } else {
    // 如果该道具类型不存在，直接添加
    gift.value.giftContent += `${typeKey}:${newGiftContent};`;
  }
  ElMessage.success('道具已成功添加到礼包');
}

const selectedGiftLabel = computed(() => {
  const selectedItem = giftOptions.value.find((item: {
    label: string;
    value: string;
  }) => item.value === giftSelect.value);
  return selectedItem ? selectedItem.label : '';  // 如果找到选中的选项，返回其 label，否则返回空字符串
});

async function handleUpload() {
  if (!gift.value.giftName) {
    ElMessage.error('请填写礼包名称');
    return;
  }
  if (!gift.value.giftDesc) {
    ElMessage.error('请填写礼包描述');
    return;
  }
  if (!gift.value.giftContent) {
    ElMessage.error('请添加道具');
    return;
  }
  await ElMessageBox.confirm('是否确认上传礼包？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).catch(() => {
    ElMessage.info('已取消');
    return;
  });
  handleLogger(`上传礼包: ${gift.value.giftName} ${gift.value.giftDesc}`);
  await AddGifts(
      props.GDGameBaseInfo.token,
      gift.value.giftName,
      gift.value.giftDesc,
      gift.value.giftContent
  ).then((res) => {
    if (res) {
      ElMessage.success('上传成功');
      handleReload();
      reSet(false);
    } else {
      ElMessage.error('上传失败');
    }
  });
}

watch(() => props.GDGameBaseInfo.data.Sids, (newSids) => {
  if (newSids) {
    giftOptions.value = newSids;
  }
});
</script>