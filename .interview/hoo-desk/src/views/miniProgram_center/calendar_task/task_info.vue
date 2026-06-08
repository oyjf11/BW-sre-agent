<template>
  <div>
    <div class="pub-form-wrap">
      <el-form :model="formData"
               ref='form'
               :rules="formRules"
               class="pub-form"
               label-width="120px"
               v-loading='formLoading'>
        <el-form-item label='任务主题'
                      prop="name">
          <el-input placeholder="请输入任务主题"
                    v-model="formData.name"></el-input>
        </el-form-item>
        <el-form-item label="简介"
                      prop="remark">
          <el-input placeholder="请输入任务简介"
                    v-model="formData.remark"></el-input>
        </el-form-item>

        <el-form-item label='日期'
                      prop='timeRange'
                      :rules='formRules.dateRules'>
          <el-date-picker v-model="timeRange"
                          type="daterange"
                          unlink-panels
                          :clearable='false'
                          range-separator="至"
                          start-placeholder="开始日期"
                          end-placeholder="结束日期"
                          @change="timeChange">
          </el-date-picker>
          <el-select v-model='timeTempIndex'
                     placeholder="日期模板"
                     filterable
                     @change='dateTempChange'>
            <el-option :label="item.tpl_name"
                       :value="index"
                       :key="item.tpl_id"
                       v-for="(item,index) in dateTempList"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if='timeRange[0]'
                      label='星期'>
          <el-checkbox :indeterminate="isIndeterminate"
                       v-model="checkAll"
                       @change="handleCheckAll">全选</el-checkbox>
          <el-checkbox @change="checkItem(item.week,index)"
                       v-for="(item,index) in weekList"
                       v-model="checkWeek"
                       :label="item.week"
                       :key="item.week">{{item.day}}</el-checkbox>
        </el-form-item>
        <el-form-item label='具体日期'
                      prop='days'
                      v-show='timeRange[0]'>
          <v-date-check ref='dateCheck'
                        :timeRange="timeRange"
                        @onChange="modelChange"
                        v-model="formData.days"></v-date-check>
        </el-form-item>
        <el-form-item label="任务星级数量">
          <el-select :disabled="true"
                     v-model="formData.star[0].star_number">
            <el-option v-for="item in starList"
                       :key='item'
                       :label="item"
                       :value="item"></el-option>
          </el-select>
          <span class="form-item-tips">暂不支持更改</span>
        </el-form-item>
        <el-form-item label='各星级名称'
                      prop="star[0].world">
          <el-row type='flex'>
            <el-col :span='3'
                    style='margin-right:10px'
                    v-for="(item,index) in formData.star[0].world"
                    :key='index'>
              <el-input placeholder="请输入名称"
                        :disabled="true"
                        v-model='formData.star[0].world[index]'></el-input>
            </el-col>
            <span class="form-item-tips">暂不支持更改</span>
          </el-row>
        </el-form-item>
        <el-form-item v-for="(item,index) in formData.child_mission"
                      :key='index'
                      :prop="'child_mission.'+index"
                      :rules="formRules.taskRules">
          <template slot="label"
                    v-if='index == 0'>子任务</template>
          <template slot="label"
                    v-else>子任务{{index}}</template>
          <el-input v-model="formData.child_mission[index].name"
                    maxlength="10"
                    placeholder="请输入子任务名称"></el-input>
          <el-button type="text"
                     maxlength="10"
                     v-if="index == formData.child_mission.length -1"
                     @click='addTask'>增加子任务</el-button>
          <el-button type="text"
                     maxlength="10"
                     v-else
                     @click='delTask(index)'>删除子任务</el-button>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
        <el-button type='primary'
                    @click='onSubmit'>提交</el-button>
        <el-button @click='cancle'>取消</el-button>
      </div>
    </div>
  </div>
</template>



<script>
import {
  getCalendarTaskInfo,
  createCalendarTaskInfo,
  updateCalendarTaskInfo
} from "@/api/miniProgram_center";
import dateCheck from "@/views/course/date_template/date_check";
import { getTemplateList } from "@/api/date_template";
export default {
  data() {
    let checkStarName = (rule, value, callback) => {
      let status = true;
      let indexArr = [];
      value.forEach((item, index) => {
        if (!item) {
          status = false;
          indexArr.push(index + 1);
        }
      });
      if (status) {
        callback();
      } else {
        let str = indexArr.join("、");
        callback(new Error("请输入星级" + str + "的名称"));
      }
    };
    let checkTask = (rule, value, callback) => {
      if (!value.name) {
        callback(new Error("请输入任务标题"));
      } else {
        callback();
      }
    };
    let checkDate = (rule, value, callback) => {
      if (!this.timeRange[0]) {
        callback(new Error("请选择时间"));
      } else {
        callback();
      }
    };
    let checkDateList = (rule, value, callback) => {
      if (value.length == 0) {
        callback(new Error("请选择具体时间"));
      } else {
        callback();
      }
    };

    return {
      isEdit: false,
      formData: {
        name: "",
        remark: "",
        star: [
          { star_number: 5, world: ["很差", "较差", "一般", "较好", "超好"] }
        ],
        child_mission: [{ name: "" }],
        days: []
      },
      formRules: {
        name: [
          {
            required: true,
            message: "请输入任务主题",
            trigger: "blur"
          }
        ],
        remark: [
          {
            required: true,
            message: "请输入简介",
            trigger: "blur"
          }
        ],
        "star[0].world": [
          {
            required: true,
            trigger: "blur",
            validator: checkStarName
          }
        ],
        days: [
          {
            required: true,
            trigger: "blur",
            validator: checkDateList
          }
        ],
        taskRules: [
          {
            required: true,
            trigger: "blur",
            validator: checkTask
          }
        ],
        dateRules: [
          {
            required: true,
            trigger: ["blur", "change"],
            validator: checkDate
          }
        ]
      },
      formLoading: false,
      timeTempIndex: "",
      starList: [1, 2, 3, 4, 5],
      dateArr: [],
      timeRange: ["", ""],
      dateTempList: [],
      weekList: [
        { day: "星期一", week: 1 },
        { day: "星期二", week: 2 },
        { day: "星期三", week: 3 },
        { day: "星期四", week: 4 },
        { day: "星期五", week: 5 },
        { day: "星期六", week: 6 },
        { day: "星期日", week: 0 }
      ],
      checkAll: false,
      checkWeek: [],
      isIndeterminate: false
    };
  },
  components: {
    "v-date-check": dateCheck
  },
  created() {
    this.getTempList();
    if (this.$route.query.id) {
      this.isEdit = true;
      this.getInfo();
    }
    let str = this.isEdit ? "编辑日历任务" : "新增日历任务";
    this.$store.dispatch("setTopTitle", {
      des: str,
      title: str
    });
  },
  methods: {
    getTempList() {
      getTemplateList({ tpl_type: 1, page: 1, size: 10000 }).then(res => {
        this.dateTempList = res.data.list;
        console.log("模板返回", res.data.list);
      });
    },
    getInfo() {
      this.formLoading = true;
      getCalendarTaskInfo({ mission_id: this.$route.query.id })
        .then(res => {
          console.log(res, "详情返回");
          this.formLoading = false;
          let data = res.data;
          if (data.days.length >= 2) {
            this.timeRange = [
              new Date(data.days[0].day),
              new Date(data.days[data.days.length - 1].day)
            ];
          } else if (data.days.length == 1) {
            this.timeRange = [
              new Date(data.days[0].day),
              new Date(data.days[0].day)
            ];
          }
          this.formData = data;
          this.formData.days = Array.from({ length: data.days.length }).map(
            (val, index) => {
              return {
                date: data.days[index].day,
                week: data.days[index].week
              };
            }
          );
        })
        .catch(e => {
          console.log(e);
          this.formLoading = false;
        });
    },
    addTask() {
      this.formData.child_mission.push({ name: "" });
    },
    delTask(index) {
      this.formData.child_mission.splice(index, 1);
    },
    onSubmit() {
      new Promise((resolve, reject) => {
        this.$refs.form.validate(valide => {
          if (valide) {
            resolve(this.isEdit);
          } else {
            reject("disable");
          }
        });
      })
        .then(isEdit => {
          let days = Array.from({ length: this.formData.days.length }).map(
            (val, index) => {
              return {
                day: this.formData.days[index].date,
                week: this.formData.days[index].week
              };
            }
          );
          let obj = {
            days: JSON.stringify(days),
            child_mission: JSON.stringify(this.formData.child_mission),
            star: JSON.stringify(this.formData.star),
            name: this.formData.name,
            remark: this.formData.remark
          };
          if (isEdit) {
            obj.mission_id = this.$route.query.id;
            return updateCalendarTaskInfo(obj);
          } else {
            return createCalendarTaskInfo(obj);
          }
        })
        .then(e => {
          console.log("创建编辑返回", e);
          let str = this.isEdit ? "编辑成功" : "新增成功";
          this.$message.success(str);
          this.$router.go(-1);
        })
        .catch(e => {
          let str = e == "disable" ? "请输入必填项" : e;
          console.log(e, "error");
          this.$message.error(str);
        });
    },
    cancle() {
      this.$router.go(-1);
    },
    timeChange() {
      this.isIndeterminate = false;
      this.checkWeek = [];
      this.checkAll = false;
    },
    modelChange(obj) {
      console.log(obj);
      let weekNum = {};
      let arr = [];
      let week = obj.list;
      let allWeekNum = obj.weekNum;
      week.forEach(item => {
        arr.push(item.week);
        if (!weekNum["week-" + item.week]) {
          weekNum["week-" + item.week] = 1;
        } else {
          weekNum["week-" + item.week] += 1;
        }
      });
      arr = Array.from(new Set(arr));
      for (let x in allWeekNum) {
        if (allWeekNum[x] != weekNum[x]) {
          let week = x.split("-")[1];
          let index = arr.indexOf(Number(week));
          if (index > -1) {
            arr.splice(index, 1);
          }
        }
      }
      if (arr.length == this.weekList.length) {
        this.checkAll = true;
      }
      this.checkWeek = arr;
    },
    dateTempChange(index) {
      let tempItem = this.dateTempList[index];
      this.timeRange = [
        new Date(Number(tempItem.start_date)),
        new Date(Number(tempItem.end_date))
      ];
      this.$refs.dateCheck.useTemplate(tempItem.date);
    },
    checkItem(val, index) {
      let checkedCount = this.checkWeek.length;
      this.checkAll = checkedCount === this.weekList.length;
      this.isIndeterminate =
        checkedCount > 0 && checkedCount < this.weekList.length;
      this.weekCheck(false, val);
    },
    handleCheckAll(val) {
      let checkVal = Array.from({ length: this.weekList.length }).map(
        (val, index) => {
          return this.weekList[index].week;
        }
      );
      this.checkWeek = val ? checkVal : [];
      this.isIndeterminate = false;
      this.weekCheck(true);
    },
    weekCheck(isAll, week) {
      let boolean = false;
      let day = week;
      if (isAll) {
        boolean = this.checkWeek.length == 0 ? false : true;
        day = "all";
      } else {
        boolean = this.checkWeek.indexOf(week) >= 0 ? true : false;
      }
      this.$refs.dateCheck.checkWeek(day, boolean);
    }
  }
};
</script>
