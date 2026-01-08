import { dict } from "@fast-crud/fast-crud";
import { shallowRef } from "vue";
import deptFormat from "/@/components/dept-format/index.vue";

/**
 * 自定义的深度合并函数，用来替代 lodash/merge。
 * 如果目标值是对象，则会将源对象的所有可枚举属性递归合并到目标对象中。
 */
function deepMerge(target: any, source: any) {
  // 如果 source 不是对象，直接返回 source（覆盖）
  if (typeof source !== "object" || source === null) {
    return source;
  }
  // 如果 target 不是对象，也直接返回 source
  if (typeof target !== "object" || target === null) {
    return source;
  }

  // 遍历 source 的 key
  for (const key of Object.keys(source)) {
    // 如果当前属性值仍是一个对象，并且不是数组，则需要递归
    if (
      typeof source[key] === "object" &&
      source[key] !== null &&
      !Array.isArray(source[key])
    ) {
      // 若 target 对应 key 不存在，则初始化为 {}
      if (!target[key] || typeof target[key] !== "object") {
        target[key] = {};
      }
      deepMerge(target[key], source[key]);
    } else {
      // 否则直接赋值，覆盖 target 里的值
      target[key] = source[key];
    }
  }
  return target;
}

/**
 * 让所有入参 (options) 变为可选:
 * 1. 先定义 defaultOptions 作为默认值（同时增加一个 sort 字段）
 * 2. 用自定义的 deepMerge 将用户传入的 options 与 defaultOptions 合并
 * 3. 将需要返回的配置项先存进数组，然后根据 sort 值排序，最后组装成对象返回
 */
export const commonCrudConfig = (options = {}) => {
  // Step 1: 定义默认配置，并为每个字段添加一个 sort。
  // 【新增】：增加 title 和 width 的默认值。
  const defaultOptions = {
    create_datetime: {
      form: false,
      table: false,
      search: false,
      sort: 10,
      title: "创建时间", // 新增
      width: 160,       // 新增
    },
    update_datetime: {
      form: false,
      table: false,
      search: false,
      sort: 20,
      title: "更新时间", // 新增
      width: 160,       // 新增
    },
    creator_name: {
      form: false,
      table: false,
      search: false,
      sort: 30,
      title: "创建人",  // 新增
      width: 100,      // 新增
    },
    modifier_name: {
      form: false,
      table: false,
      search: false,
      sort: 40,
      title: "修改人",  // 新增
      width: 100,      // 新增
    },
    dept_belong_id: {
      form: false,
      table: false,
      search: false,
      sort: 50,
      title: "所属部门", // 新增
      width: 300,      // 新增
    },
    description: {
      form: false,
      table: false,
      search: false,
      sort: 60,
      title: "备注",    // 新增
      width: 100,      // 新增
    },
  };

  // Step 2: 合并用户传入的 options 与 defaultOptions
  const finalOptions = deepMerge({ ...defaultOptions }, options);

  // 为了方便后续根据 sort 值排序，先将所有字段配置收集成一个数组
  const fieldsArray = [
    {
      key: "dept_belong_id",
      config: {
        title: "所属部门", // 原先的默认值
        type: "dict-tree",
        search: {
          show: finalOptions.dept_belong_id.search,
        },
        dict: dict({
          url: "/api/system/dept/all_dept/",
          isTree: true,
          value: "id",
          label: "name",
          children: "children",
        }),
        column: {
          align: "center",
          width: 300,
          show: finalOptions.dept_belong_id.table,
          component: {
            name: shallowRef(deptFormat),
            vModel: "modelValue",
          },
        },
        form: {
          show: finalOptions.dept_belong_id.form,
          component: {
            multiple: false,
            clearable: true,
            props: {
              checkStrictly: true,
              props: {
                label: "name",
                value: "id",
              },
            },
          },
          helper: "默认不填则为当前创建用户的部门ID",
        },
      },
    },
    {
      key: "description",
      config: {
        title: "备注", // 原先的默认值
        search: {
          show: finalOptions.description.search,
        },
        type: "textarea",
        column: {
          width: 100,
          show: finalOptions.description.table,
        },
        form: {
          show: finalOptions.description.form,
          component: {
            placeholder: "请输入内容",
            showWordLimit: true,
            maxlength: "200",
          },
        },
        viewForm: {
          show: true,
        },
      },
    },
    {
      key: "modifier_name",
      config: {
        title: "修改人", // 原先的默认值
        search: {
          show: finalOptions.modifier_name.search,
        },
        column: {
          width: 100,
          align: "center",
          show: finalOptions.modifier_name.table,
        },
        form: {
          show: false,
        },
        viewForm: {
          show: true,
        },
      },
    },
    {
      key: "creator_name",
      config: {
        title: "创建人", // 原先的默认值
        type: "text",
        search: {
          show: finalOptions.creator_name.search,
        },
        column: {
          width: 100,
          align: "center",
          show: finalOptions.creator_name.table,
        },
        form: {
          show: false,
        },
        viewForm: {
          show: true,
        },
      },
    },
    {
      key: "update_datetime",
      config: {
        title: "更新时间", // 原先的默认值
        type: "datetime",
        search: {
          show: finalOptions.update_datetime.search,
          col: { span: 8 },
          component: {
            type: "datetimerange",
            props: {
              "start-placeholder": "开始时间",
              "end-placeholder": "结束时间",
              "value-format": "YYYY-MM-DD HH:mm:ss",
              "picker-options": {
                shortcuts: [
                  {
                    text: "最近一周",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                  {
                    text: "最近一个月",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                  {
                    text: "最近三个月",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                ],
              },
            },
            // 在表单提交时，将组件的值转换为接口所需的字段
          },
          valueResolve(context: any) {
            const { value } = context;
            if (value) {
              context.form.update_datetime_after = value[0];
              context.form.update_datetime_before = value[1];
            }
          },
        },
        column: {
          width: 160,
          align: "center",
          show: finalOptions.update_datetime.table,
        },
        form: {
          show: false,
        },
        viewForm: {
          show: true,
        },
      },
    },
    {
      key: "create_datetime",
      config: {
        title: "创建时间", // 原先的默认值
        type: "datetime",
        search: {
          show: finalOptions.create_datetime.search,
          col: { span: 8 },
          component: {
            type: "datetimerange",
            props: {
              "start-placeholder": "开始时间",
              "end-placeholder": "结束时间",
              "value-format": "YYYY-MM-DD HH:mm:ss",
              "picker-options": {
                shortcuts: [
                  {
                    text: "最近一周",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                  {
                    text: "最近一个月",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                  {
                    text: "最近三个月",
                    onClick(picker: any) {
                      const end = new Date();
                      const start = new Date();
                      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                      picker.$emit("pick", [start, end]);
                    },
                  },
                ],
              },
            },
          },
          valueResolve(context: any) {
            const { value } = context;
            if (value) {
              // 假设 value 是一个数组并且 value[0] 和 value[1] 都是日期字符串
              const startDate = value[0];
              const endDate = value[1];

              // 仅示例：如果只想要“日期”部分，则可做如下处理
              if (typeof startDate === "string") {
                context.form.create_datetime_after = startDate.split(" ")[0];
              }
              if (typeof endDate === "string") {
                context.form.create_datetime_before = endDate.split(" ")[0];
              }
            }
          },
        },
        column: {
          width: 160,
          align: "center",
          show: finalOptions.create_datetime.table,
        },
        form: {
          show: false,
        },
        viewForm: {
          show: true,
        },
      },
    },
  ];

  // 【新增】：根据 finalOptions 覆盖 title 与 width
  fieldsArray.forEach((field) => {
    const key = field.key;
    // 如果 options 里配置了新的 title，就替换掉默认的
    if (finalOptions[key]?.title) {
      field.config.title = finalOptions[key].title;
    }
    // 如果 options 里配置了新的 width，就替换掉默认的
    if (finalOptions[key]?.width && field.config.column) {
      field.config.column.width = finalOptions[key].width;
    }
  });

  // 根据 finalOptions 中每个字段的 sort 值进行排序
  fieldsArray.sort((a, b) => {
    const sortA = finalOptions[a.key]?.sort ?? 0;
    const sortB = finalOptions[b.key]?.sort ?? 0;
    return sortA - sortB;
  });

  // 最后把排序好的字段再组装成一个对象返回
  const sortedResult: Record<string, any> = {};
  for (const field of fieldsArray) {
    sortedResult[field.key] = field.config;
  }

  return sortedResult;
};
