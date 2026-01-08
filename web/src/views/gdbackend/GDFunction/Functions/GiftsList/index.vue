<template>
  <fs-crud ref="crudRef" v-bind="crudBinding"/>
</template>

<script lang="ts" setup>
import {onMounted} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {GDGameBaseInfoStates} from "/@/views/gdbackend/GDFunction/gdgamebaseinfo";

const props = defineProps<{
  GDGameBaseInfo: GDGameBaseInfoStates;
}>();
const {crudBinding, crudRef, crudExpose} = useFs({
  createCrudOptions: (crudExpose) => createCrudOptions({
    crudExpose, GDGameBaseInfo: props.GDGameBaseInfo
  })
});


// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>