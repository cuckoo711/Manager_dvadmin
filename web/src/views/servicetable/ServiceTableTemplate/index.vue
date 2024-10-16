<!--suppress ALL -->
<template>
  <fs-page>
    <div>
      <el-container>
        <el-card shadow="always" style="width: 100%;">
          <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <el-tag style="font-size: 16px; margin-right: auto;">添加新的开服表模板</el-tag>
          </div>
          <el-table :data="[{}]" style="width: 100%">
            <el-table-column
                label="渠道"
                align="center"
                header-align="center"
                width="240"
            >
              <template #default="scope">
                <el-tooltip
                    class="box-item"
                    effect="dark"
                    content="请选择模板对应渠道"
                    placement="bottom"
                >
                  <el-select placeholder="请选择渠道" clearable filterable v-model="serviceTemplateSelectedChannelId"
                             style="width: 200px">
                    <el-option v-for="channel in serviceTemplateChannelOptions" :key="channel.value" :label="channel.label"
                               :value="channel.value"/>
                  </el-select>
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column
                label="模板表头字段"
                align="center"
                header-align="center"
                min-width="260"
            >
              <template #default="scope">
                <el-tooltip
                    class="box-item"
                    effect="dark"
                    content="
                        请按照以下格式填写模板表头字段：<br>
                        ### 注意, 空格请使用 '&&' 代替 ###<br>
                        标签信息：<br>
                        - 游戏名：game_name<br>
                        - 游戏 ID：game_id<br>
                        - 开服名称：open_name<br>
                        - 开服日期时间：open_datetime_格式<br>
                        - 开服日期：open_date_格式<br>
                        - 开服时间：open_time_格式<br>
                        - 开服编号：open_id<br><br>

                        时间格式：<br>
                        - 年：yyyy<br>
                        - 月：MM<br>
                        - 日：dd<br>
                        - 时：HH<br>
                        - 分：mm<br>
                        - 秒：ss<br><br>

                        请按顺序填写模板表头字段，以逗号分隔，例：<br>
                        game_id, open_name, open_datetime_yyyy-MM-dd HH:mm, open_id<br>
                        此例表示模板表头字段为：游戏ID、开服名称、开服日期时间（年-月-日 时:分）、开服编号<br><br>

                        注意：模板表头字段必须与上传的模板文件表头字段完全一致。
    "
                    placement="bottom"
                    raw-content

                >
                  <el-input
                      v-model="serviceTemplateHeaderFields"
                      :rows="1"
                      type="textarea"
                      placeholder="请输入模板表头字段"
                  />
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column
                label="是否分表"
                align="center"
                header-align="center"
                min-width="80"
            >
              <template #default="scope">
                <el-tooltip
                    class="box-item"
                    content="如选择分表，将按照游戏将数据分表存储，否则将存储在同一张表中"
                    placement="bottom"
                >
                  <el-switch v-model="serviceTemplateIsSplitTable" active-value="1" inactive-value="2"
                             active-text="是" inactive-text="否" style="margin-left: 10px;"/>
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column
                label="上传模板"
                align="center"
                header-align="center"
                min-width="120"
            >
              <template #default="scope">
                <el-tooltip
                    class="box-item"
                    effect="dark"
                    content="仅支持上传 .xlsx 或 .xls 格式文件"
                    placement="bottom"
                >
                  <el-upload
                      ref="serviceTemplateUploadRef"
                      name="file"
                      accept=".xlsx,.xls"
                      :show-file-list="true"
                      :auto-upload="false"
                      :before-remove="serviceTemplateBeforeRemoveFile"
                      :on-remove="serviceTemplateOnRemoveFile"
                      :on-exceed="serviceTemplateHandleFileExceed"
                      :limit="1"
                      v-model:file-list="serviceTemplateUploadedFileList"
                  >
                    <el-button type="primary">选择文件</el-button>
                  </el-upload>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" style="margin: 10px; float: right;" @click="serviceTemplateSubmit">
            提交
          </el-button>
        </el-card>
      </el-container>
    </div>
    <div :style="{height: 'calc(100% - 240px)'}">
      <fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
    </div>
  </fs-page>
</template>

<script lang="ts">
import {defineComponent, onMounted, ref} from "vue";
import {UploadFilled} from "@element-plus/icons-vue";
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {request} from "/@/utils/service";
import {ElMessage, ElMessageBox, genFileId, UploadFile, UploadInstance, UploadProps, UploadRawFile} from "element-plus";
import {uploadTemplate} from "./api";

export default defineComponent({
  name: 'ServiceTableTemplate',
  components: {UploadFilled},
  setup() {
    const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions});
    const serviceTemplateChannelOptions = ref<{ value: string; label: string }[]>([]);
    const serviceTemplateSelectedChannelId = ref<string>('');
    const serviceTemplateUploadInstance = ref<UploadInstance>();
    const serviceTemplateUploadedFileList = ref<UploadFile[]>([]);
    const serviceTemplateHeaderFields = ref<string>('');
    const serviceTemplateIsSplitTable = ref<string>('0');

    onMounted(async () => {
      crudExpose.doRefresh();
      await serviceTemplateFetchChannelOptions();
    });

    const serviceTemplateBeforeRemoveFile: UploadProps['beforeRemove'] = async (uploadFile) => {
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

    const serviceTemplateOnRemoveFile: UploadProps['onRemove'] = (_) => {
      serviceTemplateUploadedFileList.value = [];
    };

    const serviceTemplateHandleFileExceed: UploadProps['onExceed'] = (files) => {
      serviceTemplateUploadInstance.value?.clearFiles();
      const file = files[0] as UploadRawFile;
      file.uid = genFileId();
      serviceTemplateUploadInstance.value?.handleStart(file);
    };

    const serviceTemplateFetchChannelOptions = async () => {
      const response = await request({
        url: '/api/channel_manage/?page=1&limit=99999',
        method: 'get',
      });
      serviceTemplateChannelOptions.value = response.data.map((item: any) => ({
        value: item.id,
        label: item.name,
      }));
    };

    const serviceTemplateValidateFileSize = (size: number) => {
      return size <= 1024 * 1024 * 10;
    };

    const serviceTemplateShowConfirmation = async (message: string) => {
      return await ElMessageBox.confirm(message, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).catch(() => false);
    };

    const serviceTemplateSubmit = async () => {
      if (!serviceTemplateSelectedChannelId.value) {
        ElMessage.error('请选择渠道');
        return;
      }
      if (!serviceTemplateHeaderFields.value) {
        ElMessage.error('请输入模板表头字段');
        return;
      }
      if (!serviceTemplateUploadedFileList.value.length) {
        ElMessage.error('请上传模板文件');
        return;
      }
      const size = serviceTemplateUploadedFileList.value[0].size || 0;
      if (!serviceTemplateValidateFileSize(size)) {
        ElMessage.error('文件大小不能超过 10MB');
        return;
      }
      const confirm = await serviceTemplateShowConfirmation('确定提交模板？');
      if (!confirm) {
        return;
      }
      const file: any = serviceTemplateUploadedFileList.value[0].raw || serviceTemplateUploadedFileList.value[0];
      try {
        const formData = new FormData();
        formData.append('channel_id', serviceTemplateSelectedChannelId.value);
        formData.append('fields', serviceTemplateHeaderFields.value);
        formData.append('is_split', serviceTemplateIsSplitTable.value);
        formData.append('file', file);
        await uploadTemplate(formData);
        ElMessage.success('提交成功');
      } catch (e) {
        ElMessage.error('提交失败');
        console.error(e);
      }
      await crudExpose.doRefresh();
    }

    return {
      crudBinding,
      crudRef,
      crudExpose,
      serviceTemplateChannelOptions,

      serviceTemplateSelectedChannelId,
      serviceTemplateHeaderFields,
      serviceTemplateUploadedFileList,
      serviceTemplateUploadInstance,
      serviceTemplateIsSplitTable,

      serviceTemplateBeforeRemoveFile,
      serviceTemplateOnRemoveFile,
      serviceTemplateHandleFileExceed,
      serviceTemplateSubmit,
    }
  },
})
</script>