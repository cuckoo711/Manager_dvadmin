<template>
  <el-watermark :content="watermarkContent" :gap="[200, 200]">
    <div class="home-container">
      <el-row :gutter="15" class="home-card-one mb15">
        <el-col
            :xs="24"
            :sm="12"
            :md="12"
            :lg="6"
            :xl="6"
            v-for="(v, k) in homeOne"
            :key="k"
            :class="{ 'home-media home-media-lg': k > 1, 'home-media-sm': k === 1 }"
        >
          <div class="home-card-item flex">
            <div class="flex-margin flex w100" :class="`home-one-animation${k}`">
              <div class="flex-auto">
              <span class="font30">
                <CountUp :target="v.num1" :duration="800"/>
              </span>
                <span class="ml5 font16" :style="{ color: v.color1 }">
                <template v-if="v.num2 > 0">
                  +<CountUp :target="v.num2" :duration="800"/>
                </template>
                <template v-else-if="v.num2 < 0">
                  <CountUp :target="v.num2" :duration="800"/>
                </template>
                <template v-else>

                </template>
              </span>
                <div class="mt10">{{ v.num3 }}</div>
              </div>
              <div class="home-card-item-icon flex" :style="{ background: `var(${v.color2})` }">
                <i
                    class="flex-margin font32"
                    :class="v.num4"
                    :style="{ color: `var(${v.color3})` }"
                ></i>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="15" class="home-card-two mb15">
        <el-col :xs="24" :sm="14" :md="14" :lg="16" :xl="16">
          <div class="home-card-item">
            <div style="height: 100%" ref="homeLineRef"></div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="10" :md="10" :lg="8" :xl="8" class="home-media">
          <div class="home-card-item">
            <div style="height: 100%" ref="homePieRef"></div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="15" class="home-card-three">
        <el-col :xs="24" :sm="10" :md="10" :lg="8" :xl="8">
          <div class="home-card-item">
            <div class="home-card-item-title">快捷导航</div>
            <div class="home-monitor">
              <div class="flex-warp">
                <!--
                  给 flex-warp-item-box 绑定 @click 事件，
                  当点击时调用 onClickNavItem()
                -->
                <div class="flex-warp-item" v-for="(v, k) in homeThree" :key="k">
                  <div
                      class="flex-warp-item-box"
                      :class="`home-animation${k}`"
                      @click="onClickNavItem(v.value)"
                  >
                    <div class="flex-margin">

                      <el-icon>
                        <component :is="v.icon" :style="{ color: v.iconColor }"></component>
                      </el-icon>
                      <span class="pl5">{{ v.label }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="14" :md="14" :lg="16" :xl="16" class="home-media">
          <div class="home-card-item">
            <div style="height: 100%" ref="homeBarRef"></div>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-watermark>
</template>

<script lang="ts">
import {
  defineComponent,
  markRaw,
  nextTick,
  onActivated,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  toRefs,
  watch,
  computed,
} from 'vue';
import * as echarts from 'echarts';
import {storeToRefs} from 'pinia';
import {useThemeConfig} from '/@/stores/themeConfig';
import {useTagsViewRoutes} from '/@/stores/tagsViewRoutes';
import {getData} from '/@/views/system/home/api';
import {useRoutesList} from '/@/stores/routesList';
import CountUp from './CountUp.vue';
// 如果要在点击时进行路由跳转，需要引入你的路由实例
// 假设你的路由在 /@/router/index.ts
import {useRouter} from 'vue-router';
import {
  Bell,
  Box,
  Cpu,
  CreditCard,
  DataAnalysis,
  DataLine,
  Download,
  Finished,
  FolderChecked,
  MessageBox,
  Paperclip,
  Plus,
  ToiletPaper,
  Top,
  Files,
  LocationInformation
} from "@element-plus/icons-vue";

export default defineComponent({
  name: 'home',
  components: {
    Top,
    Bell,
    Box,
    Cpu,
    CreditCard,
    DataAnalysis,
    DataLine,
    Download,
    Finished,
    FolderChecked,
    MessageBox,
    Paperclip,
    Plus,
    ToiletPaper,
    CountUp,
    Files,
    LocationInformation
  },
  setup() {
    // ========== 路由实例 ==========
    const router = useRouter();

    // ========== 获取路由 store ==========
    const stores = useRoutesList();
    const {routesList} = storeToRefs(stores);

    // 创建一个列表，用于存储所有的路由（在 path 字段里，包括每一级的 children）
    const allRoutes = ref<string[]>([]);

    /**
     * 递归函数，用于将所有路由的 path 字段提取出来
     * @param routes 路由数组
     */
    const getRoutes = (routes: any[]) => {
      routes.forEach((route) => {
        // 收集当前路由的 path
        allRoutes.value.push(route.path);

        // 递归收集 children
        if (route.children && route.children.length > 0) {
          getRoutes(route.children);
        }
      });
    };

    // ========== 根据需求，维护一份原始的快捷导航数据 ==========
    const originalHomeThree = [
      {
        icon: markRaw(ToiletPaper),
        label: '请假申请',
        value: '/leave',
        iconColor: '#FF9800', // 更鲜艳的橙色
      },
      {
        icon: markRaw(MessageBox),
        label: '生成授权书',
        value: '/authorization/Authorizationletter',
        iconColor: '#FF5252', // 鲜亮的红色
      },
      {
        icon: markRaw(Bell),
        label: '生成公告',
        value: '/authorization/Notice',
        iconColor: '#E91E63', // 带有粉调的亮色
      },
      {
        icon: markRaw(FolderChecked),
        label: '上传对接表',
        value: '/manage/upload_dddd',
        iconColor: '#FF5722', // 明亮的橘红色
      },
      {
        icon: markRaw(DataLine),
        label: '对账详情',
        value: '/incomedata/view',
        iconColor: '#9C27B0', // 明度较高的紫色
      },
      {
        icon: markRaw(CreditCard),
        label: '官斗操作',
        value: '/gamebackend/gd/function',
        iconColor: '#2196F3', // 亮蓝色
      },
      {
        icon: markRaw(Box),
        label: '大圣合服',
        value: '/gamebackend/dslh/mergeserver',
        iconColor: '#4CAF50', // 清爽的绿色
      },
      {
        icon: markRaw(Download),
        label: '下载中心',
        value: '/downloadCenter',
        iconColor: '#F44336', // 鲜艳的红色
      },
      {
        icon: markRaw(Finished),
        label: '生成开服计划',
        value: '/service_table/plan',
        iconColor: '#FFC107', // 亮黄色
      },
      {
        icon: markRaw(DataAnalysis),
        label: '日报看板',
        value: '/daily/view',
        iconColor: '#8BC34A', // 明度更高的黄绿色
      },
      {
        icon: markRaw(Paperclip),
        label: 'Quick后台',
        value: '/Quick/QuickOrderList',
        iconColor: '#03A9F4', // 亮天蓝色
      },
      {
        icon: markRaw(Cpu),
        label: '服务器',
        value: '/consoles',
        iconColor: '#FF9800', // 再次使用鲜艳的橙色
      },
      {
        icon: markRaw(Files),
        label: '运营活动',
        value: '/tools/activity_manage',
        iconColor: '#FF5252', // 再次使用鲜亮的红色
      },
      {
        icon: markRaw(LocationInformation),
        label: '域名转IP',
        value: '/tools/domain2ips',
        iconColor: '#E91E63', // 再次使用带有粉调的亮色
      }
    ];

    // 引用 DOM 元素
    const homeLineRef = ref<HTMLElement | null>(null);
    const homePieRef = ref<HTMLElement | null>(null);
    const homeBarRef = ref<HTMLElement | null>(null);

    // Pinia store
    const storesTagsViewRoutes = useTagsViewRoutes();
    const storesThemeConfig = useThemeConfig();
    const {themeConfig} = storeToRefs(storesThemeConfig);
    const {isTagsViewCurrenFull} = storeToRefs(storesTagsViewRoutes);

    // 响应式状态
    const state = reactive({
      homeOne: [
        {
          num1: 0,
          num2: 0,
          num3: '盈利版号',
          num4: 'iconfont icon-ditu',
          color1: '#6690F9',
          color2: '--next-color-success-lighter',
          color3: '--el-color-success',
        },
        {
          num1: 0,
          num2: 0,
          num3: '盈利游戏',
          num4: 'fa fa-meetup',
          color1: '#6690F9',
          color2: '--next-color-primary-lighter',
          color3: '--el-color-primary',
        },
        {
          num1: 0,
          num2: 0,
          num3: '昨日流水',
          num4: 'iconfont icon-zaosheng',
          color1: '#6690F9',
          color2: '--next-color-warning-lighter',
          color3: '--el-color-warning',
        },
        {
          num1: 0,
          num2: 0,
          num3: '昨日日活',
          num4: 'fa fa-github-alt',
          color1: '#6690F9',
          color2: '--next-color-danger-lighter',
          color3: '--el-color-danger',
        },
      ],
      // 初始化为空数组，后续根据权限进行过滤
      homeThree: [] as {
        icon: any;
        label: string;
        value: string;
        iconColor: string;
      }[],
      myCharts: [] as echarts.ECharts[],
      charts: {
        theme: '',
        bgColor: '',
        color: '#303133',
      },
      last30Days: [] as string[], // 过往30天的日期数组
    });

    // 存储获取的数据
    const datas = ref({
      all_games_count: 0,
      all_games_ratio: 0,
      all_banhaos_count: 0,
      all_banhaos_ratio: 0,
      all_recharge: 0,
      all_recharge_ratio: 0,
      all_actives: 0,
      all_actives_ratio: 0,
      daily_recharge: [] as number[], // 单日充值数据
      daily_actives: [] as number[], // 单日日活数据
      daily_subscribers: [] as number[], // 单日新增数据
      daily_devices: [] as number[], // 单日设备数据
      daily_payments: [] as number[], // 单日付费数据
      weekly_daily_recharge: [] as number[], // 7日内充值数据
      monthly_daily_recharge: [] as number[], // 30日内充值数据
      banhaos_recharge: {} as Record<string, number>, // 各版号充值数据
    });

    /**
     * 生成过往30天的日期数组（不包括今天）
     * 格式：'MM-DD'
     * @returns 日期数组
     */
    const generateLast30Days = (): string[] => {
      const dates: string[] = [];
      const today = new Date();
      for (let i = 30; i >= 1; i--) {
        const pastDate = new Date(today);
        pastDate.setDate(today.getDate() - i);
        const month = pastDate.getMonth() + 1;
        const day = pastDate.getDate();
        const formattedDate = `${month < 10 ? '0' + month : month}-${
            day < 10 ? '0' + day : day
        }`;
        dates.push(formattedDate);
      }
      return dates;
    };

    // 在 setup 中初始化 last30Days
    state.last30Days = generateLast30Days();

    /**
     * 初始化图表
     * @param chartRef 图表容器引用
     * @param initFunction 初始化函数
     */
    const initChart = (chartRef: HTMLElement | null, initFunction: () => void) => {
      if (chartRef) {
        // 查找是否已有对应的图表实例
        const existingChart = state.myCharts.find(
            (chart) => chart.getDom() === chartRef
        );
        if (existingChart) {
          existingChart.dispose();
          state.myCharts = state.myCharts.filter((chart) => chart !== existingChart);
        }
        // 初始化新的图表
        initFunction();
      } else {
        console.warn('图表引用为 null:', chartRef);
      }
    };

    /**
     * 初始化折线图
     */
    const initLineChart = () => {
      initChart(homeLineRef.value, () => {
        const chart = echarts.init(homeLineRef.value!, state.charts.theme);
        const option = {
          backgroundColor: state.charts.bgColor,
          title: {
            text: '过往30天流水趋势',
            left: 'left',
            textStyle: {fontSize: 15, color: state.charts.color},
          },
          grid: {top: 70, right: 20, bottom: 30, left: 80},
          tooltip: {trigger: 'axis'},
          legend: {data: ['单日流水', '前7日平均日流水', '前30日平均日流水'], right: 0},
          xAxis: {
            type: 'category',
            data: state.last30Days,
          },
          yAxis: [
            {
              type: 'value',
              name: '金额',
              splitLine: {show: true, lineStyle: {type: 'dashed', color: '#f5f5f5'}},
            },
          ],
          series: [
            {
              name: '单日流水',
              type: 'line',
              symbolSize: 6,
              symbol: 'circle',
              smooth: true,
              data: datas.value.daily_recharge,
              lineStyle: {color: '#87ffa9'},
              itemStyle: {color: '#87ffa9', borderColor: '#87ffa9'},
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {offset: 0, color: '#87ffa9b3'},
                  {offset: 1, color: '#87ffa903'},
                ]),
              },
            },
            {
              name: '前7日平均日流水',
              type: 'line',
              symbolSize: 6,
              symbol: 'circle',
              smooth: true,
              data: datas.value.weekly_daily_recharge,
              lineStyle: {color: '#fe9a8b'},
              itemStyle: {color: '#fe9a8b', borderColor: '#fe9a8b'},
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {offset: 0, color: '#fe9a8bb3'},
                  {offset: 1, color: '#fe9a8b03'},
                ]),
              },
            },
            {
              name: '前30日平均日流水',
              type: 'line',
              symbolSize: 6,
              symbol: 'circle',
              smooth: true,
              data: datas.value.monthly_daily_recharge,
              lineStyle: {color: '#9E87FF'},
              itemStyle: {color: '#9E87FF', borderColor: '#9E87FF'},
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {offset: 0, color: '#9E87FFb3'},
                  {offset: 1, color: '#9E87FF03'},
                ]),
              },
            },
          ],
        };
        chart.setOption(option);
        state.myCharts.push(chart);
      });
    };

    /**
     * 基于 HSL 动态生成颜色数组
     * @param count 需要的颜色数量
     * @returns 颜色字符串数组 (如 ['hsl(0, 60%, 60%)', 'hsl(36, 60%, 60%)', ...])
     */
    function generateHslColors(count: number): string[] {
      const colors: string[] = [];
      for (let i = 0; i < count; i++) {
        const hue = Math.round((i * (360 / count)) % 360);
        const saturation = 60;
        const lightness = 60;
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
      }
      return colors;
    }

    /**
     * 生成“x月各版号流水占比”标题
     * 基准日期为当前日期的前一天
     */
    function getPreviousMonthChartTitle(): { year: number; month: number; day: number } {
      const now = new Date();
      now.setDate(now.getDate() - 1); // 前一天
      return {
        year: now.getFullYear(),
        month: now.getMonth() + 1,
        day: now.getDate(),
      };
    }

    const watermarkContent = computed (() => {
      const dateobj = getPreviousMonthChartTitle()
      return [`当前页面数据截止至`, `${dateobj.year}年${dateobj.month}月${dateobj.day}日 00时05分00秒`, `数据来自QuickSDK与后台汇总计算`];
    });

    /**
     * 初始化饼图
     */
    const initPieChart = () => {
      initChart(homePieRef.value, () => {
        const chart = echarts.init(homePieRef.value!, state.charts.theme);

        // 1. 取出 banhaos_recharge 数据并构建 { name, value } 形式的 data
        const banhaosData = datas.value.banhaos_recharge || {};
        const banhaoNames = Object.keys(banhaosData);
        const banhaoValues = banhaoNames.map((name) => Number(banhaosData[name]) || 0);

        // 2. 计算总流水，用于计算占比
        const totalRecharge = banhaoValues.reduce((acc, val) => acc + val, 0);

        // 3. 生成 ECharts 需要的 data
        const data = banhaoNames.map((name, index) => {
          const val = banhaoValues[index];
          return {
            name,
            value:
                totalRecharge === 0
                    ? 0
                    : Number(((val / totalRecharge) * 100).toFixed(2)),
            rawValue: val,
          };
        });

        // 4. 动态生成颜色数组 (这里使用 HSL 分布)
        const colorList = generateHslColors(data.length);

        const previous = getPreviousMonthChartTitle()
        const option = {
          backgroundColor: state.charts.bgColor,
          title: {
            text: `${previous.year}年${previous.month}月 各版号流水占比`,
            left: 'left',
            textStyle: {fontSize: 15, color: state.charts.color},
          },
          tooltip: {
            trigger: 'item',
            formatter: (params: any) => {
              const rawValue = (params.data as any).rawValue.toFixed(2);
              return `${params.name}<br/>占比：${params.value}%<br/>流水：${rawValue}`;
            },
          },
          graphic: {
            elements: [
              {
                type: 'image',
                z: -1,
                style: {
                  image: themeConfig.value.isIsDark
                      ? ''
                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAK0AAACtCAYAAADCr/9DAAAcoElEQVR4Xu19e7wcRZn28/ZM90xXzzknOYEkIAEiBAUUFyFc4wKCCAt8gHhBUEDFG8K3Iri6+3ETL0hQ9FthvYC4gAb0cwFRQcUlKiIIbpRbEBGUREJIyHWmq2e6Z+r9fjU5iQnJOWcuPV195nT/l5yq93nep57p6amueouQXV0rwMzW6tWrS4XCsFvPVQWIyAphKweR3ShUGw2EAwMIAfhE1OgacJIHoEme/7jpM3O+UgnnWFZuDpF6pQJ2JtDOBJ4JwgxmmgbwEABr3GAAM1Ah8CqAVgC8nEBLFWgJQz1Liv7sefZTRBS0EGvSNslMu9nQL1u2TEyZsv3rARygwK8nxuvIwh7McBJ0iL4T/xXgR8DW75nxcL2ef2jKFFqTIIdUQ01q02qTDg5v/wZLqSMZ9I8AtGHtFI6YAmExFO4jsu6N3Ny9Q0SrU8gzEUqTzrSrV8ud7aJ1okW54wg4jJmLiSgdL4i+Gz8Moh9xQ91ZKhUeizd8uqNNCtNKya9QqnYqWdbbAcwF0Fd5M/AnZv5/UFgwMFBYnG7Ldc+urwZvczmY2Q6CxolMfDaYjwKQ616uCRHhd2BcX63at0ybRusnBOM2SfadaYOAd2Wun8PgMwFMb1OPvmlORBUGfw8K13qes6hvEuunr0nfD/dn4gsJdAqAfD8NUpe5MBF+wWR9QRRydxMRdxnPePcJf6etBNGRFvNFDBxuXM20EyA8QWx9xnVz3yMilXa6o/GbsKYNgugNivlzAOZNVPGN8SY8rpgvK7nObRPxzjvhTFsu1/ay8rgKTP9kbND7BZixyLLoQte1F06klCaMadetWzecz7uXg/DB7Jk1bovRD3JW42PFYvHZuCP3Il7qTcvMJKvRe8D0eYC374UIWcymAlUwf14I5/NEVEuzJqk27bp11Tm2bV3HwGFpFrGfuDHwlKLG+wdd97605pVK0+q7axBE/8zAZwGItIrXx7wUA9esWfXiJ2fNmpW6FWepM63v8w6M6EYivKmPTTExUiM8wQ2cXio5j6SJcKpMu96vnZQj6zqAt0uTSJOcS41B/+a5+S+lZXosFaZduJDzcw+MPk/Ax/rpLV1/mZ1+FLn5M6aQ+XW9xk1bLvN0ykXfpeyN1kTw+F9Y4WTTjwtGTavXC4DodoB3mggjlnFsrun0AT5LiML3TelhzLRS1t7KoBuz2QFTQ98VrgLzJZ5X0LM7iV9GTCtl+FEGvtjiZsDERckAW1SAcN1DD9rnHHEE1VvsEUuzxE1bkbX5BPp4LOyzIOYVYP6hEM7biaiaFJnETKtrA8hq9DUw3p9UchlOMgro9bpu0T5BLzxPAjER0zJzTlajG8A4I4mkMozkFSDggWq1cuzw8PC6XqP33LT6DhtUo/9kxrt7nUwW37gCD/iVtUdPnz69p3fcnpvW98PrQXifcTkzAokoQET3rnpp+fG9XLPQU9NKGX2RwfotV3ZNIgWY+S5POCcRUdSLtHtm2oqMLiTwVb0gncVMvwIM3Oq59mm9WK/QE9NKWX8HQy2YZPOwzIz1ROQDqqbvMrp4HYAiQLqKjS5SN1lqLzQ/VQSeL0ThE3F/xGI3rZTRwQzWe44KcZM1Ha9ZS4D5CRAeJcZitqxnuK6WAOGLnue9RDT6JLv+QVoul4cLhYHpzPVZjQbvRkSvAngfxdiHCMOm8+sBPoNwtuc6N8QZO1bTrpJyVhH2wwDPiJOkqVjMWG0R7mELv2LLvt+z8Vivtl5Xq9XdmfOHKqh5YD4GoL5Yj0GEEExHCmH/Oq5xjM20upCbDCK9RWP/uMiZiEOEv0DXxYJ1h+vmHzJVBLlcq72GFE4gJl1/7B9MaBEj5ouE+v5CiL/FETM20/p+eJ3+KoiDVNIxGCgT4RZifEsI58Gk8cfDq1Z5j7oK30OwzgR4h/Hap/TvDwjXPiyOGYVYTFsJwncT46aUijUqLQKeZsaXhLBvTuoVZDca6R92QdA4iaEuAHBQN7FM9CXQ1ULYmntXV9emXVetzrHZ+h9mDHTFJMHOzHiEiS8vuc4dvXpG7XU6UkaHKlaXENHRvcaKMT6DreM9L39XNzG7Mq3+5Mugfj/AB3RDIqm+uo6rBesi1819vxfzh0nlsTmOlNE8Bl8xccpD0YvCzb+WiFZ2qldXpvWD6FIwX9YpeFL9mLHWIvq06+avISJ9ykzfXXpuHFBXMrBL2pMj0B1C2Cd3yrNj01Yq4T+QhYdSekbBZnrwf4Hr53me90KnIk2UfsuXL/dKg8OXE/DPaX+RwcTvKrmF73SibUembS41DCJtWH2wRiovZqxQxB8aFIXbU0mwh6R8358L2P8Jwl49hOkyNL2kGvm9Bgbaf0zoyLRSRh9jsN4uk86L+W6lnLMGBvRZXZPz0vPmQRB9gYFz0rotnwg3C9dpe41126aVUu7EyD8JoJRCOzT0M7YQzmf75YdWtxo3N5ASfROMwW5j9aA/W0RHtltqtAPThrcwcGoPEugyJK1hhXeWSvZPuwzUd911Td9cnu5gxpzUJUd4/KEH7X3b2RzZlmmljA5hsH6H3Fa/3gvFf1UNHDcZjiPqVEtmHg6C6HYG9CF/6boYH/E85z9aJdWy+Zp1YoPoAQAHtho8iXbM/Aewc0ypRC8mgTeRMZi5IGW4AERvSVkeK4Vr707U2hFSLZtWytopDDJWVWQUkR8Urn0sEa1N2SCkls7IJlP9jKuPrErPxfwZzytc3Aqhlkw7sv37cTD2bCVoQm30AoyjJ8KagYT0aBlmZDyvB+M9LXfqfcOKatR2GxgYGHfGpyXTVoLaacTU0URwj3JdFNb8I6dOnZrdYTsUWBvXD6LvUIp+VOvtWUIU/mW8lMY1bTM5GT5ORCm5y/KzquEc1Mmk9HhiTLa/66NYfRn9OC0FrPW3Zj0KZg8ODr401liMa9r1snZyDnRbOgaUXmpYjUMHi8U/pYPPxGfBzEO+jO4nwt6pyIb5cs8rXNqVaaUMf8PAwSlIqG4RHeW69i9TwKWvKAQB76K4/rt0VGCnVcLN70xEcjSRx7zTShkexICe5jJ+sVIXlErFq40T6VMClWp0FCn+SRoW2ijGOQOe89VOTbuAgXeaHye+zRMFfVBzdvVQAd+vXQyiy3sI0VJoZiwuec6ojyuj3mnL5fL0XL6whNn0VnD6Wz3Kv25oiFa3lHHWqGMF9ByuH0QLCXhDx0Fi6qiIDh8Y5VFwVNNWZPXjBGt+TBw6DaMXVLzJde3/7jRA1q89BfTzbYOjxwhmt08RsEAI5/RtsR/VtH4QLjb+MoFwvec6WT3b9nzXdWvfDz8CwjVdB+ouQBDW7B2nTt36bec2TeuH4f6o4+HuMLvszbw8FM6eU7NXtF0K2X735huzDTUsDmm/d4w9GB/0POcbL4+4TdNWZO0qAl0YI3zboSyyznLdvD5IJLsMKDCynep3JmcTGPhlSTiHj2va5rm01egvzAY3yDEeFsI+MFvIbcCtm0H6fvh1ED5gkIWSHM3a3vOWbc5hqzvtSAG53xgkCovo8OwlgskR2IDt+/4OIPvPRo/NYpzrec61Y5u2Gs1nxeZOn2H83POc7DBn855tMpCydhWbfFQk3OO5zhYFSba60/p++BgIrzGlGYEOFcI2eqc3lXsacZl5uyCI/sqAZ4hfrbzenjZzpq77u+HawrRSylmM/HMGt9Pc7wlnniFxMthRFPD98BoQPmJMIMs6wSvmf7RN0/p++H4QtppiSIwsWyd7Xv6OxPAyoJYUqFZ5t4aKnjI4k/AfnnA2fWi2uNNWZKhPA9f1UA1cvES4zuyJWhDOgGCJQvoy+gHA/ytR0I2PA4Q/Cdd51bbvtDL6G8CvMEFM1yvwvMKnjGBnoOMq4PvV40HWD8dt2JsGrBr2zI3FVzbdadcGwWybc8/2BnPcqKpWrc8eHhZLxm2ZNTCiQHNDpAyXgshIUWcCv0WMlLjaZNogqJ+uWH3bhCIE/EII5wgT2Blm6wpIGV3N4PNb7xFfSwJ9QQi7ORW7ybS+rF8DKDO/ENss1hCfFFmkdhQw+eKJQPcLYTdnljYzbajnRk1sq2GCPUsIer4dAbO2ySuwoWBL/XlD5z74wrUH9Q/1pmlHVvWsh5kJ5Ec94bwu+SHIEDtRwPfDb4Lw3k76dtsnZ6lXF4vFp5qmXVutvtJW1jPdBu2kP4Pnl3pwql8nXLI+4ytQlrVTLdAt47eMvwWBTxGicFvTtL5fPx6kjExnsEXHlIpZpcP4h7g3ESuVykyyHL3qatzyA7EzILrYc+3PNIErsno+wTKx07UhXHsqEZVjTzAL2DMFpAyfZmD3ngGMFphxk+c5Z47cacNrQc2K0YlezHii5DnGFuckmmwfgckgvJkZ7zKQUnNtygbTyuiHAB+fNAkiLBDutjevJc0lw2tdASnD8xlI/JuZQH8Twp614fHADx8hwj6t046nJYE+KYR9ZTzRsihJKVCpRG8ii3+WFN5mOPpxsrjxTrsC4O0TJ8HqRM8r3pk4bgbYlQJS8ixGZOSVO8HeiRYu5PwBB0Y1AFZXmXTQmRXvUyoVHuuga9bFoAIj8/oBACdxGoz9SFeSsXIFI6XfhWsPZEWREx/2WAB9WXsaoMRnEFipN1O1Wt2joSy9wDfZi7HW85ypyYJmaHEpUJGhLp+01fbuuOKPFofA7yDfD/cHJV+YQx+uXBJ/X9jb62Sz+PEqYGzDAOMDVC4Hh1m53C/iTamlaL/1hHNQSy2zRqlTwA/Cr4HxwaSJ6XN/qVKpHkOWdbcB8IVCOG9MGjfDi0cBKcOrGUh8ba2eJiXfrx4HsjbtdIwnpRaiEP3Ec+1jW2iZNUmhAhVZu0IbKHFqRBeR79dOBJGBHbB8pycKJyaedAYYiwK+X7sMRGOejRAL0MuDEF1m7k7L/GPPKyT+6rgnQk7CoL5f+xSILkk8deZLTZr2p55XOCbxpDPAWBSoyNqVBBr3zK9YwDYLwuB/pSCIjlDM98YdvIV4v/aEY7xMegs8sybbUEDK8N8ZOC9pcQh0AZk6wYYZj5U8J/FFOkmL3K94MghvYsa7E8/PwoepVqu9pt4gA+//6QVP2DsmnnQGGIsCfhDdBebEZ3+Y+F0kJe/EiJbGkkl7QerNZWZEjfa6Za3ToIAvw0UA9k2aCyt1LC1btkwMTdluUxnFJElUg/rO06YJEx+YJNPsS6yKH75EhGmJJ8eYO7KeNtR7tEpJExjrrKikuWR4rSuwevXqoUKxZOQEeIvs2U3TyiB8mtnARjULH/SKW59e0rp8WUsTCvh+OBeEh0xgN5ezamBTy8wAXOsJ51wTyWeYnStQCcKziPGtziN02pPWeMIeHtkjVruRiM7oNFSn/Ri4ryScf+y0f9bPjAIVGf5fAv63AfRmNaINz7RBdAmYE68NS4SKW2zWPagbECCD7FABX4b6ZHoDy0rpdk/Yb2maNgjqpylW3+kwh+66Mfb3POd/uguS9U5KAWZ2ZRDpH2GJ7w8ji64SRftfNtxpw3A/1KFP50v8YqjzS6L45cSBM8COFAiC6DDFbGLTgC7E9D7PdW7YWDVRyCDSVRNzHWXSRSdmvrvkFf6pixBZ1wQVKPu1T1tEFyUIuQmKgIOFcB7cVERMBuEfmbHpMIYESQXCtYeJqJogZgbVoQK+DPVB3/t32L2bbg2/Yk+ZPp0qfzetDG9h4NRuonbcl9UJnldMfvdEx4QnZ0cp5U4j58wlXyMD/FRJFF6tld9k2oqMLiTwVUaGg3CT5zpnGsHOQFtWwFQNL02Qwd8uiUJzVdkm066Xcl4O+ftaziDGhsxYv3LF8zNmz56dPSLEqGvcoXwZPgjgwLjjthKPoM4TonjNFqZl5uLIVEahlSBxt2HFp5VKBSMVpuPOpR/jlcu1Pa0cPWGkmLIWNI/Xe47z+y1Mq/9RkeGvCDCym4CBhaVsS3lq/S5l9EUGf8wMQVor3Py0jad5blGC3A+iT4E5+c1qG5TgRl3tOThYTL5Ek5mRmDCoS5cudYenzVwC8HZmSNOdnrA37dx+2Snk0TwGG3mu1WJYhK+7rvMhM8JkqKMpYPqgbwLOE8JpPs9u9XjAzHlfRiuJMMXQEAaqUdt1YGBghSH8DPZlCuiynn4QLSYYmcNvsqlHao+hoeLT2zSt/k8pw1sZeIep0dPTbkIUEt+abCrftONWgtppxGRmXcqGX31PCeE052fHMG3tnQxaYFBMySrcrVQqLTfIIYPecChiLqhGi5mxhylBNi6SGdO0zFwKqvUXmVmYIgpY13oiny0ONzcATWTfD84G5a4zSYPyOEg4zm/HNO0GsrXvg+gUg2TrqsH7DgwUHjfIYVJDr1y5ckB4g08BtIMpIYjwnFu0ZxMRj2taKetvY6jvmSLbxCX6uefabzLKYRKDSxnNZ3DzqHpTF4GuFMLeqjLjNo+K1NvKB4e2e4EIg6YIa1yLcIbrOjeb5DAZsf0w3Bf15sbFvMn8VYNfu61v21HPNy374TcswvtNkmbGKk/YexLRSpM8JhO2nvaUQaSfIV9vNG/Gw57nHLAtDqOaVsrwAAa2eAA2kgTznZ6X1bFNSvuyX/uUZaKE58sTHKO8wJgnSfsy1Hu3zH7idDKMD3ue87WkBm6y4qyX8tA88r9gw48FAK3zK2t2mj59eqWtO61uHAThexTjhhQMomSFQ0sl5w8p4NKXFJh5uyCIfsfALilI8CuecEbdoj7mnZaZCzKoPwfwjBQk8qxw7f2JaE0KuPQVBf0SQVbrPwHzUSlIrFGP1KuHhop/Ho3LmKbVnfwguhjMl6cgGT0Ndo8o5o8joigVfPqEhJTRlxj80XSkw7d7ovCWsbiMa9p163g4b0fPmShQt03ijBs8z3lfOgSe+CykDM9l4CtpyYSAA4VwxqwTNq5pdTIVWZtPIKMTzVuIyvxpzyuYWveblvHtmoeUtVMY9F0TpQO2RZ4Z95Q85+jxEmvJtCOHPj8LwBsvYFJ/14dUCGGb2YiZVJI9xPH96rEg63YARrZXbXtWgOYJYd8/Xtotmbb5bOvXPgeifx0vYIJ/Z333F8L+YoKYfQGlDUtW7r90iaPUJMR8t9di0ZaWTbuGeYoTRM8AGE5NopoI0WWeaydePC9VGrRBpixrp1horo9NzR0WgGKF/Vqd0mzZtBuebcOPEvClNjRKpinjq0LY52XnN4wtd9kPP2xR80dX4uWvxmTGuNHznLNaNUtbpn3iCXZ2mR0+TqA5rQIk1o75LimdU7ffnnQp/uzaTAE9D+sH0XwCDO2mHXM4fIL9KiHo+VYHrS3T6qDVanRMQ3Hip5a3lBDjSaX4lIGBwpMttZ8EjZh5WFbDBWB6cxrTZaJ/K7n2Fe1wa9u0OriU0W0MPrkdoKTaMlC2wB8QonBrUphpxZEyOoShFgCUhlezW8nE4Kc819mHiMJ2NOzQtHInhbzeoTnQDliSbQm42XXtc4lIlzCdVNfChZw/4KD6RWD+P6bXxI4hPCuiNw64dtu1bjsyrSbi++E5IFybcjcsgWWd4xXzP045z9joVSo1fef6JshIOc7W8yBc77lOR+u1OzYtM+vDoO9l4PDWmZppyeDvWmhcIIRo+WHfDNPOUVes4JIohZcQSK8hsDuPlEjPpbVq5bXDw8PrOkHr2LQabE0Q7Gqr3COmt+W0kjgRlRnqqvK6NVfPnDnTyAmVrfBst82GFVrRmVD8GZC5TYht8FYW0dGua/93G322aNqVaXWkShCeQYwbOyWQfD9eTqDPua593USuPq4rv1SC8K0W0aVg7JW8jp0hMvDlknDO76z3hl5dm7ZpXBl+m4DTuyGSdF9mvEjgaxqN2lcHBwdXJY3fKZ4uyVqR0Rk5C+czY4vKK53GTLDfomXPP3fInDlzat1gxmJavUfeKw09NAFFBBH5DL6FGNcLsWVRiG6Ejbvvump195yiswnWewHePu74vY7HjHWNnJo7VPx7Ta5OMWMxrQav1Wp7N5T1oK5Q0ykZ0/0Y/Eci61ZVV99LwwsKn3lHDqK3EfB2AAfH9c1oQGdW4LcOiMJtcWDHZlpNRsra20bWZ8YaN45E247BeJKI7lIW7vEK+d/oH3Jtx2izw9NPP12Y8YpXzM1x7kgiOpaBubr8Q5th0tec+bOeV4jtGKfYzeX7tU/D0DlTPRytBoBHwc0t9Y8Q0aNRJP84NDS0ulPMFStWlDxvyhzLsvZpsNrHAh3AYH3UUbHTmOnsR3cKN3/yxirecXCM3bQj87e6XKj+Suv3S88z/oWZl1sWrVSMVcRcgYUqM+o5siwFFJnZI8I0KF1Jm2YwsCsRJtxzaQeD+YfyenvezJkU6xRj7KbViW0odz7j5wAO6SDRrEtfKMBLwPWDPc9bFnc6PTGtJrmWeWpehvcR0d5xk87ipV6Bl/I5PqxQKCzuBdOemVaT9X1/R7Ls+5jxyl6Qz2KmUoG1YBzpec6iXrHrqWmbd9y1wWzbsX4J0KxeJZHFTYcCRFQB481C2L/pJaOem1aTX7euunvepnsz4/ZyKM3G1i9pGnWcMDBgL+w1k0RMq5MIAp6tONTG3bXXSWXxk1VAz2ETcLzr2r9KAjkx0+pk9CnWinM/I6I9k0guw0hCAVpVBx83lOAr8ERNqyVk5mkyiH4E4KAkJM0weqkAL1ENHDsw0JtZgtGYJ27aEeO6MqgvAPikXkqaxe6pAr8H28d7HsU+DzseayOmHTGuFQThlQy6YAIvBBlP3z79O93pV9acPlrR414nbcy0GxPTi8gt0NdSVaKn16pP3PgM5iuEcC6Ocy1Bu3IYN60m7PvhfiD+fjaz0O7wJdder4dl4vfGtbywG+apMK1OQL/2tYPwWwBtOiK9m8SyvrEqsChn2e8oFmnU6tyxoo0TLDWm3cizLMNzLWA+gPRU9EtyRNKFpRj4d8+1P9FuQY1eppE60+pky+XaXlaObgKwXy+Tz2KPqcBSVvTeUsnWq/VSdaXStCOzC3k/qF9A4Euzu26inlEgfF0U7U+mtTpPak27cZiq1erudWV9g4AjEh26yQjGeLJB9Q8MCvHrNKefetOO3HXJ98PTybKuAHinNAs6EbkxYz2YP/fCC0u+3O327iTynxCm3SgEMwtZrX8C3DwdO/uh1r1DGmgWWoku8jzvhe7DJRNhQpl2oyRS8iwmfb4ZdPXotNetSmYk20NhgH/Mii5utWR8e+F723pCmvbvz7v8ykYjuoQIp5s/z7W3AxVbdKKfEvMl453VFRteDwJNaNNuZt7dGxx9HIwz+m8LdiyjrgC6k8BXCuE8GEtEg0H6wrQb9SuXebqVr38IjA8BvINBXVMBrauiE3Bjo66+MjhY/FMqSMVAoq9Mu9kPNrsShCdZZJ0N5iNTd5pLDAM3TohFYFwnpf2dfjw4pS9Nu/mASilnKcq9i0CngfGa3vvFGMJSBt+KHL5dKhQeNcYiAeC+N+3mGpZrtb0shVNY0UlE2Heir+Mlwp9B9AMo3Oa6+QeIiBPwjHGISWXazdX2fd4RiI4lwlEMvBHAdOOjMQ4B/YwK5vssop/V6/zTwcHCH9POuRf8Jq1pXy5muVzb08rTPCg+CBbNBUNvvsz3QvQWYzIB+hDthxXUb4mt+4WwF2WnUsZUCbzFQZhQzZr1yGbM2Jsb2Nti3pMZc0C0GzN2IcKUGJPxwVgComcY/Azp9/+NxuJ6PXi004M0YuSWylDZnbaDYdGFo2u12g5K5WbUWW1nWTTFYgwo6OqIVgEKNpPKE6MGywqJEQJcY4ZPZK1pEK9GXa1Qylk+NEQdlwvtgHpfdPn/ixNifr4QLGYAAAAASUVORK5CYII=',
                  width: 230,
                  height: 230,
                },
                left: '16.5%',
                top: 'center',
              },
            ],
          },
          legend: {
            type: 'scroll',
            orient: 'vertical',
            right: '0%',
            left: '65%',
            top: 'center',
            itemWidth: 14,
            itemHeight: 14,
            data: banhaoNames,
            textStyle: {
              rich: {
                name: {
                  fontSize: 14,
                  fontWeight: 400,
                  width: 200,
                  height: 35,
                  padding: [0, 0, 0, 60],
                  color: state.charts.color,
                },
                rate: {
                  fontSize: 15,
                  fontWeight: 500,
                  height: 35,
                  width: 40,
                  padding: [0, 0, 0, 30],
                  color: state.charts.color,
                },
              },
            },
          },
          series: [
            {
              type: 'pie',
              radius: ['60', themeConfig.value.isIsDark ? '90' : '110'],
              center: ['32%', '50%'],
              label: {show: false},
              labelLine: {show: false},
              itemStyle: {
                color: (params: any) =>
                    colorList[params.dataIndex % colorList.length],
              },
              data,
            },
          ],
        };

        chart.setOption(option);
        state.myCharts.push(chart);
      });
    };

    /**
     * 初始化柱状图
     */
    const initBarChart = () => {
      initChart(homeBarRef.value, () => {
        const chart = echarts.init(homeBarRef.value!, state.charts.theme);
        const option = {
          backgroundColor: state.charts.bgColor,
          title: {
            text: '过往30天玩家数据',
            left: 'left',
            textStyle: {fontSize: 15, color: state.charts.color},
          },
          tooltip: {trigger: 'axis'},
          legend: {data: ['当天日活', '当日新增用户', '当日新增设备', '当日付费用户'], right: 0},
          grid: {top: 60, right: 80, bottom: 30, left: 80},
          xAxis: [
            {
              type: 'category',
              data: state.last30Days,
              boundaryGap: true,
              axisTick: {show: false},
            },
          ],
          yAxis: [
            {
              type: 'value',
              name: '数量',
              nameLocation: 'middle',
              nameTextStyle: {padding: [3, 4, 50, 6]},
              splitLine: {
                show: true,
                lineStyle: {type: 'dashed', color: '#f5f5f5'},
              },
              axisLine: {show: false},
              axisTick: {show: false},
              axisLabel: {color: state.charts.color, formatter: '{value} '},
            },
          ],
          series: [
            {
              name: '当天日活',
              type: 'bar',
              data: datas.value.daily_actives,
              barWidth: 25,
              yAxisIndex: 0,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {offset: 0, color: 'rgba(108,80,243,0.3)'},
                  {offset: 1, color: 'rgba(108,80,243,0)'},
                ]),
                // 柱状图圆角
                borderRadius: [30, 30, 0, 0],
              },
            },
            {
              name: '当日新增用户',
              type: 'line',
              data: datas.value.daily_subscribers,
              smooth: true,
              yAxisIndex: 0,
              itemStyle: {color: '#FF6462'},
            },
            {
              name: '当日新增设备',
              type: 'line',
              data: datas.value.daily_devices,
              smooth: true,
              yAxisIndex: 0,
              itemStyle: {color: '#6690F9'},
            },
            {
              name: '当日付费用户',
              type: 'line',
              data: datas.value.daily_payments,
              smooth: true,
              yAxisIndex: 0,
              itemStyle: {color: '#FFA500'},
            },
          ],
        };
        chart.setOption(option);
        state.myCharts.push(chart);
      });
    };

    /**
     * 批量调整图表大小
     */
    const resizeCharts = () => {
      nextTick(() => {
        state.myCharts.forEach((chart) => {
          chart.resize();
        });
      });
    };

    /**
     * 初始化窗口大小调整事件
     */
    const initEchartsResize = () => {
      window.addEventListener('resize', resizeCharts);
    };

    /**
     * 移除窗口大小调整事件
     */
    const removeEchartsResize = () => {
      window.removeEventListener('resize', resizeCharts);
    };

    /**
     * 初始化比率显示
     * @param ratio 比率字符串
     * @returns 格式化后的比率字符串
     */
    function init_ratio(ratio: string) {
      return ratio === '0' ? '0' : !ratio.startsWith('-') ? `+${ratio}` : ratio;
    }

    /**
     * 填充数据数组，确保长度为指定长度
     * @param data 原始数据数组
     * @param targetLength 目标长度
     * @returns 填充后的数据数组
     */
    const fillData = (data: number[], targetLength: number): number[] => {
      const filledData = [...data];
      while (filledData.length < targetLength) {
        filledData.push(0);
      }
      return filledData.slice(0, targetLength);
    };

    // 点击事件：跳转到对应路径
    const onClickNavItem = (path: string) => {
      console.log('用户点击快捷导航: ', path);
      // 此处使用 router 跳转，可根据实际需求更改为新窗口、或外部链接等
      router.push(path);
    };

    // 页面加载时
    onMounted(async () => {
      try {
        datas.value = await getData();

        const setColor = (num2: number): string => {
          return num2 > 0 ? '#6690F9' : '#FF6462';
        };

        // 更新 homeOne 的数据项，并根据 num2 设置 color1
        state.homeOne.forEach((item, index) => {
          switch (index) {
            case 0:
              item.num1 = datas.value.all_banhaos_count;
              item.num2 = Number(init_ratio(String(datas.value.all_banhaos_ratio)));
              break;
            case 1:
              item.num1 = datas.value.all_games_count;
              item.num2 = Number(init_ratio(String(datas.value.all_games_ratio)));
              break;
            case 2:
              item.num1 = datas.value.all_recharge;
              item.num2 = Number(init_ratio(String(datas.value.all_recharge_ratio)));
              break;
            case 3:
              item.num1 = datas.value.all_actives;
              item.num2 = Number(init_ratio(String(datas.value.all_actives_ratio)));
              break;
            default:
              break;
          }
          item.color1 = setColor(item.num2);
        });

        // 填充折线图的数据，确保长度为30
        datas.value.daily_recharge = fillData(datas.value.daily_recharge, 30);
        datas.value.weekly_daily_recharge = fillData(datas.value.weekly_daily_recharge, 30);
        datas.value.monthly_daily_recharge = fillData(datas.value.monthly_daily_recharge, 30);
        datas.value.daily_actives = fillData(datas.value.daily_actives, 30);
        datas.value.daily_subscribers = fillData(datas.value.daily_subscribers, 30);
        datas.value.daily_devices = fillData(datas.value.daily_devices, 30);
        datas.value.daily_payments = fillData(datas.value.daily_payments, 30);

        // 等待 DOM 更新后初始化图表
        await nextTick();
        initLineChart();
        initPieChart();
        initBarChart();
        initEchartsResize();
      } catch (error) {
        console.error('获取数据失败:', error);
      }
    });

    // 由于页面缓存原因，keep-alive 时重新调整图表大小
    onActivated(() => {
      resizeCharts();
    });

    // 组件卸载前清理资源
    onBeforeUnmount(() => {
      state.myCharts.forEach((chart) => chart.dispose());
      removeEchartsResize();
    });

    // 监听主题变化，重新初始化图表
    watch(
        () => themeConfig.value.isIsDark,
        async (isIsDark) => {
          state.charts.theme = isIsDark ? 'dark' : '';
          state.charts.bgColor = isIsDark ? 'transparent' : '';
          state.charts.color = isIsDark ? '#dadada' : '#303133';
          await nextTick();
          // 重新初始化图表以应用主题变化
          initLineChart();
          initPieChart();
          initBarChart();
        },
        {
          immediate: true,
        }
    );

    // 监听 tagsview 全屏状态变化，调整图表大小
    watch(
        () => isTagsViewCurrenFull.value,
        () => {
          resizeCharts();
        }
    );

    // 核心：监听 routesList 变化后，用 allRoutes 收集可访问路径，再筛选 originalHomeThree
    watch(
        () => routesList.value,
        (newRoutes) => {
          allRoutes.value = [];
          if (Array.isArray(newRoutes) && newRoutes.length > 0) {
            getRoutes(newRoutes);
          }
          // 筛选出可访问的路由
          const canAccessPaths = allRoutes.value;
          // 根据 canAccessPaths 来筛选原始的 homeThree
          state.homeThree = originalHomeThree.filter((item) =>
              canAccessPaths.includes(item.value)
          );
        },
        {immediate: true}
    );

    return {
      homeLineRef,
      homePieRef,
      homeBarRef,
      onClickNavItem, // 记得返回该方法，供模板中使用
      watermarkContent,
      ...toRefs(state),
    };
  },
});
</script>

<style scoped lang="scss">
$homeNavLengh: 12;
.home-container {
  overflow: hidden;
  padding-top: 10px;

  .home-card-one,
  .home-card-two,
  .home-card-three {
    .home-card-item {
      width: 100%;
      height: 100px;
      border-radius: 4px;
      transition: all ease 0.3s;
      padding: 10px;
      overflow: auto;
      background: var(--el-color-white);
      color: var(--el-text-color-primary);
      border: 1px solid var(--next-border-color-light);

      &:hover {
        box-shadow: 0 2px 12px var(--next-color-dark-hover);
        transition: all ease 0.3s;
      }

      &-icon {
        width: 70px;
        height: 70px;
        border-radius: 100%;
        flex-shrink: 1;

        i {
          color: var(--el-text-color-placeholder);
        }
      }

      &-title {
        font-size: 15px;
        font-weight: bold;
        height: 30px;
      }
    }
  }

  .home-card-one {
    @for $i from 0 through 3 {
      .home-one-animation#{$i} {
        margin-bottom: 10px;
        opacity: 0;
        animation-name: error-num;
        animation-duration: 0.5s;
        animation-fill-mode: forwards;
        animation-delay: calc($i/10) + s;
      }
    }
  }

  .home-card-two,
  .home-card-three {
    .home-card-item {
      height: 350px;
      width: 100%;
      overflow: auto;

      .home-monitor {
        height: 100%;

        .flex-warp-item {
          width: 25%;
          height: 100px;
          display: flex;

          .flex-warp-item-box {
            margin: auto;
            text-align: center;
            color: var(--el-text-color-primary);
            display: flex;
            border-radius: 5px;
            background: var(--next-bg-color);
            cursor: pointer;
            transition: all 0.3s ease;

            &:hover {
              background: var(--el-color-primary-light-9);
              transition: all 0.3s ease;
            }
          }

          @for $i from 0 through $homeNavLengh {
            .home-animation#{$i} {
              opacity: 0;
              animation-name: error-num;
              animation-duration: 0.5s;
              animation-fill-mode: forwards;
              animation-delay: calc($i/25) + s;
            }
          }
        }
      }
    }
  }
}
</style>
