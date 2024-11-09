<template>
  <fs-page>
    <div>
      <el-container>
        <el-card shadow="always" style="width: 100%;">
          <el-collapse v-model="isCollapsed">
            <el-collapse-item name="1" title="更新映射表">
              <el-upload
                  ref="upload"
                  name="file"
                  drag
                  accept=".xlsx"
                  :show-file-list="true"
                  :before-remove="beforeRemove"
                  :on-remove="handleRemove"
                  :limit="1"
                  :on-exceed="handleExceed"
                  :auto-upload="false"
                  v-model:file-list="fileList"
              >
                <el-icon class="el-icon--upload">
                  <upload-filled/>
                </el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或<em>点击添加</em>
                </div>
              </el-upload>
              <el-button type="primary" @click="submitUpload">
                提交
              </el-button>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-container>
    </div>
    <div :style="{height: 'calc(100% - 95px)'}">
      <fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
    </div>
  </fs-page>
</template>

<script lang="ts" setup name="ServiceTableMap ">
// ServiceTableMap Page - Auto-generated on 2024-10-16 15:36:48
import {ref, onMounted} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {UploadFilled} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox, genFileId, UploadFile, UploadInstance, UploadProps, UploadRawFile} from "element-plus";
import {uploadMap} from "/@/views/servicetable/ServiceTableMap/api";

const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions});
const isCollapsed = ref<string[]>([]);
// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
const upload = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([]);
const beforeRemove: UploadProps['beforeRemove'] = async (uploadFile) => {
  return ElMessageBox.confirm(
      `取消上传 ${uploadFile.name} ?`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
  ).then(
      () => {
        return true;
      }
  ).catch(
      () => {
        return false;
      }
  );
};
const handleRemove: UploadProps['onRemove'] = (_) => {
  fileList.value = [];
};

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}
const ShowConfirmation = async (message: string) => {
  return await ElMessageBox.confirm(message, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).catch(() => false);
};

const submitUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.error('请上传文件')
    return
  }
  const size = fileList.value[0].size || 0;
  if (size > 1024 * 1024 * 10) {
    ElMessage.error('文件大小不能超过10M')
    return
  }
  const confirm = ShowConfirmation('确定要上传文件吗?');
  if (!confirm) {
    return
  }

  const loadingMessage = ElMessage({
    message: '正在上传中，请稍候（请不要关闭页面或刷新）...',
    type: 'info',
    showClose: false,
    duration: 0,
  });
  const file: any = fileList.value[0].raw || fileList.value[0];
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await uploadMap(formData);
    ElMessage.success('已提交上传文件' + response.message);
  } catch (e) {
    ElMessage.error(`上传失败: ${e}`);
  }
  await crudExpose.doRefresh();
  loadingMessage.close();
}

</script>