<template>
  <fs-page>
    <el-main>
      <el-form inline label-width="auto" label-position="top" width="100%">
        <el-row :gutter="20" style="width: 100%">
          <el-col :span="12">
            <el-form-item label="原链接">
              <el-input
                  v-model="inputText"
                  placeholder="请输入原链接, 按行分割"
                  @input="onInputChange"
                  type="textarea"
                  :rows="maxRows"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="输出结果">
              <el-input
                  v-model="outputText"
                  placeholder="请在左侧输入原链接后查看结果"
                  :readonly="true"
                  type="textarea"
                  :rows="maxRows"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button-group style="margin-top: 10px;float: right; ">
            <el-button @click="clearForm" type="warning">清空</el-button>
            <el-button @click="copyToClipboard" type="primary">复制输出结果</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-main>
  </fs-page>
</template>
<script setup>
import {computed, ref} from "vue";
import {ElInput, ElMessage} from "element-plus";
import {GetDomainIps} from "/@/views/tools/domainips/api";

const inputText = ref("");
const outputText = ref("");

const maxRows = computed(() => {
  return Math.floor(window.innerHeight / 29);
});

const onInputChange = async () => {
  await GetDomainIps(inputText.value).then((res) => {
    outputText.value = res.ips;
  });
};

const clearForm = () => {
  inputText.value = "";
  outputText.value = "";
};

const copyToClipboard = () => {
  if (!outputText.value) {
    ElMessage.warning("没有内容可复制");
    return;
  }
  navigator.clipboard.writeText(outputText.value).then(() => {
    ElMessage.success("复制成功");
  }).catch(() => {
    ElMessage.error("复制失败");
  });
};


</script>