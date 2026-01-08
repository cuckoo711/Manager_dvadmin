<template>
  <el-container style="height: 100%">
    <el-header style="padding: 10px">
      <el-row>
        <el-upload
            ref="upload"
            :limit="1"
            :http-request="handleFileRead"
            :show-file-list="false"
            :on-exceed="handleExceed"
            accept=".xlsx"
            drag
        >
          <template #trigger>
            <el-tooltip content="仅支持单个xlsx文件导入" placement="bottom-start">
              <el-button type="primary">选择文件</el-button>
            </el-tooltip>
          </template>
        </el-upload>
        <el-button-group style="padding-left: 10px">
          <el-button type="warning" @click="clearFiles">重置</el-button>
        </el-button-group>
        <span style="padding-left: 10px">
          <el-tag v-if="fileName">
            当前文件: {{ fileName }}
          </el-tag>
        </span>
      </el-row>
    </el-header>
    <el-main>
      <el-table :data="pagedData" style="width: 100%" height="calc(100%)">
        <!--        <el-table-column type="index" width="70" label="序号" align="center"/>-->
        <el-table-column v-for="col in columns" :key="col.prop" :prop="col.prop" :label="col.label"
                         :width="col.width" show-overflow-tooltip/>
      </el-table>
    </el-main>
    <el-footer>
      <el-row justify="space-between">
        <el-pagination
            size="small"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            :page-size="pageSize"
            :total="getTotal()"
            :current-page="currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
        <el-button class="ml-3" type="success" @click="submitUpload">
          确定上传
        </el-button>
      </el-row>
    </el-footer>
  </el-container>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue';
import {
  ElMessage,
  ElMessageBox,
  genFileId,
  type UploadInstance,
  type UploadProps,
  type UploadRawFile
} from 'element-plus';
import * as XLSX from 'xlsx';
import {GDGameBaseInfoStates} from '/@/views/gdbackend/GDFunction/gdgamebaseinfo';
import {CheckConfigExist, UploadConfig} from "/@/views/gdbackend/GDFunction/Functions/AddActivity/api";

const emit = defineEmits(['reload', 'logger', 'close']);

const props = defineProps<{ GDGameBaseInfo: GDGameBaseInfoStates }>();

// function handleReload() {
//   emit('reload');
// }

function handleColse() {
  emit('close', '关闭');
}

function handleLogger(log: string, push: boolean = true) {
  emit('logger', log, push);
}

// 当前选择的菜单信息
const selectOptions: any = ref({name: null});
const fileData = ref<any>(null);
// 文件名称
const fileName = ref();
// 分页参数
const currentPage = ref(1);
const pageSize = ref(50);
// 表头
const columns = ref();
// 正确的列名
const requiredColumns = ['活动类型ID', '名称', '活动描述', '活动开始时间', '活动结算时间', '活动结束时间', '活动参数'];

// 计算分页后的数据
const pagedData = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;
  if (fileData.value) {
    return fileData.value.slice(startIndex, endIndex);
  }
  return [];
});

// 分页事件处理
const handleSizeChange = (newSize: any) => {
  pageSize.value = newSize;
  currentPage.value = 1; // 重置为第一页
};

const handleCurrentChange = (newPage: any) => {
  currentPage.value = newPage;
};

const getTotal = () => {
  return fileData.value ? fileData.value.length : 0;
};

const upload = ref<UploadInstance>();

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  upload.value!.handleStart(file);
};

async function submitUpload() {
  if (!fileData.value || fileData.value.length === 0) {
    ElMessage.warning('请选择文件');
    return;
  }

  // 为列定义类型
  const uploadedColumns = columns.value.map((col: { prop: string; label: string }) => col.prop);

  // 检查列名是否一致
  const invalidColumns = uploadedColumns.filter((col: string) => !requiredColumns.includes(col));
  const missingColumns = requiredColumns.filter(col => !uploadedColumns.includes(col));

  if (invalidColumns.length > 0 || missingColumns.length > 0) {
    ElMessage.error('上传的文件列名不符合模板要求，请使用正确的模板格式。');
    return;
  }

  // 数据预处理
  const data = fileData.value.map((item: any) => {
    const itemTemp = JSON.parse(JSON.stringify(item));
    const {'活动开始时间': startTime, '活动结束时间': endTime, '活动结算时间': settleTime} = itemTemp;
    itemTemp['活动开始时间'] = startTime.split(' ')[0];
    itemTemp['活动结束时间'] = endTime.split(' ')[0];
    itemTemp['活动结算时间'] = settleTime.split(' ')[0];
    return itemTemp;
  });

  // 列名映射
  const columnMap: { [key: string]: string } = {
    '活动类型ID': 'activityId',
    '名称': 'name',
    '活动描述': 'description',
    '活动开始时间': 'startTime',
    '活动结算时间': 'settleTime',
    '活动结束时间': 'endTime',
    '活动参数': 'params',
  };
  data.forEach((item: any) => {
    Object.keys(item).forEach((key) => {
      item[columnMap[key]] = item[key];
      delete item[key];
    });
  });

  // 数据分类
  const dataDict: { [key: string]: any[] } = {'Alone': [], 'District': [], 'Cross': [], 'Normal': []};
  data.forEach((item: any) => {
    const {'activityId': activityId, 'settleTime': settleTime, 'endTime': endTime} = item;
    if (
        (activityId > 400 && activityId < 500) ||
        activityId === 1000 ||
        (Number(settleTime) > 30000000 && Number(endTime) > 30000000)
    ) {
      dataDict['Alone'].push(item);
    } else if (activityId > 1200 && activityId < 1299) {
      dataDict['District'].push(item);
    } else if (activityId > 1300 && activityId < 1399) {
      dataDict['Cross'].push(item);
    } else {
      dataDict['Normal'].push(item);
    }
  });

  const jsonData = JSON.stringify(dataDict);

  // 检查是否已存在配置
  const isExist = await CheckConfigExist(props.GDGameBaseInfo.token);
  if (isExist.exist) {
    try {
      await ElMessageBox.confirm('已存在活动配置，是否覆盖？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      });
    } catch (e) {
      ElMessage.info('取消上传');
      return; // 明确中断后续逻辑
    }
  }

  // 上传数据
  await UploadConfig(props.GDGameBaseInfo.token, jsonData).then((res) => {
    if (res.status === 2000) {
      handleLogger(`上传游戏[${props.GDGameBaseInfo.data.GameName}]活动配置成功`);
      ElMessage.success('文件上传成功！');
      handleColse()
    } else {
      ElMessage.error('文件上传失败！');
    }
  });
}

// 处理时间转换
function convertToSeconds(time: string, standardTime: string) {
  const timeDiff = (new Date(time).getTime() - new Date(standardTime).getTime()) / 1000;
  return String(timeDiff >= 30000000 ? 31536000 : timeDiff);
}

function formatTime(seconds: number): string {
  const days = Math.floor(seconds / (60 * 60 * 24));
  const hours = Math.floor((seconds % (60 * 60 * 24)) / (60 * 60));
  const minutes = Math.floor((seconds % (60 * 60)) / 60);
  const secs = seconds % 60;

  return `${days}日 ${hours}时${minutes}分${secs}秒`;
}

// 文件读取逻辑
function handleFileRead({file}: { file: File }) {
  clearFiles();
  const reader = new FileReader();
  reader.onload = async (e) => {
    const data = new Uint8Array(e.target?.result as ArrayBuffer);
    const workbook = XLSX.read(data, {type: 'array', raw: true});
    const sheet = workbook.Sheets[workbook.SheetNames[0]];

    let json: { [key: string]: any }[] = XLSX.utils.sheet_to_json(sheet);
    const uploadedColumns = Object.keys(json[0] || {});
    const invalidColumns = uploadedColumns.filter((col: string) => !requiredColumns.includes(col));
    const missingColumns = requiredColumns.filter(col => !uploadedColumns.includes(col));

    if (invalidColumns.length > 0 || missingColumns.length > 0) {
      ElMessage.error('上传的文件列名不符合模板要求，请使用正确的模板格式。');
      clearFiles();
      return;
    }

    json = json.filter((item: any) => Object.values(item).some((value: any) => value !== null && value !== undefined && value !== ''));

    if (json.length !== 0) {
      const standardTime = json[0]['活动开始时间'];

      json = json.map((item: any) => {
        const {'活动开始时间': startTime, '活动结束时间': endTime, '活动结算时间': settleTime} = item;

        item['活动开始时间'] = convertToSeconds(startTime, standardTime);
        item['活动结束时间'] = convertToSeconds(endTime, standardTime);
        item['活动结算时间'] = convertToSeconds(settleTime, standardTime);

        item['活动开始时间'] += ` (${formatTime(item['活动开始时间'])})`;
        item['活动结算时间'] += ` (${formatTime(item['活动结算时间'])})`;
        item['活动结束时间'] += ` (${formatTime(item['活动结束时间'])})`;

        return item;
      });
    }

    fileData.value = json;
    columns.value = Object.keys(fileData.value[0] || {}).map(key => ({
      prop: key,
      label: key,
      width: 'auto',
    }));
    //第一列宽度100
    columns.value[0].width = 100;

    fileName.value = file.name;
    // console.log(fileData.value);
  };

  reader.readAsArrayBuffer(file);
}

function clearFiles() {
  fileData.value = [];
  columns.value = [];
  fileName.value = '';
  upload.value!.clearFiles();
}

onMounted(() => {
});

defineExpose({selectOptions});
</script>
