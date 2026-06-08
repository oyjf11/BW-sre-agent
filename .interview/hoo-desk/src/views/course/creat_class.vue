<template>
  <v-form-wrap>
    <el-form
      ref="form"
      slot="form"
      v-loading="formLoading"
      :rules="classInfoRules"
      :model="class_info"
      class="pub-form"
      label-width="120px"
    >
      <div class="tips-bar">班级信息</div>
      <el-form-item label="课程模版">
        <el-select
          v-model="class_info.chooseCourse"
          filterable
          placeholder="课程模版"
          @change="selectCourse"
        >
          <el-option
            :label="item.course_name"
            :value="index"
            :key="index"
            v-for="(item,index) in tempList"
          >
            <span class="course-name-left">{{ item.course_name }}</span>
            <span class="course-name-right">
              {{typeLabel[item.attend_type]}}
              <span v-if="item.is_open==0">(下架)</span>
              <span v-else-if="item.is_open==1">(上架)</span>
            </span>
          </el-option>
        </el-select>
        <el-button class="form-tips-btn" type="text" @click="toCourseTemp">立即新增</el-button>
      </el-form-item>
      <el-form-item prop="org_grade">
        <div class="setting-wrap">
          <i class="hoo hoo-feedback_fill"></i>
          <strong v-show="class_info.org_subject != ''">科目: </strong>
          <span>{{ class_info.org_subject }}</span>
          <strong v-show="class_info.org_grade != ''">年级: </strong>
          <span>{{ class_info.org_grade }}</span>
          <strong v-show="class_info.org_term != ''">学期: </strong>
          <span>{{ class_info.org_term }}</span>
        </div>
      </el-form-item>
      <!-- <el-form-item label="阶段" prop="org_grade">
        <el-input v-model="class_info.org_grade" :disabled="true"></el-input>
      </el-form-item>
      <el-form-item label="科目" prop="org_subject">
        <el-input v-model="class_info.org_subject" :disabled="true"></el-input>
      </el-form-item>
      <el-form-item label="学期" prop="org_term">
        <el-input v-model="class_info.org_term" :disabled="true"></el-input>
      </el-form-item> -->
      <el-form-item label="班级名称" prop="class_name">
        <el-input @focus="classNameFocus" v-model="class_info.class_name"></el-input>
      </el-form-item>
      <el-form-item label="教师" prop="teacher_id"
      >
        <el-select
          @change="teacherChange"
          v-model="class_info.teacher_id"
          filterable
          placeholder="教师"
        >
          <el-option
            :label="teacher.nickname + ' '+ teacher.phone"
            :value="teacher.user_id"
            :key="teacher.user_id"
            v-for="(teacher) in teacher_list"
          >
            <span style="float:left">{{teacher.nickname}}</span>
            <span style="float:right">{{teacher.phone}}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="助教">
        <el-select
          :disabled="relationTeacherDisabled"
          multiple
          v-model="class_info.relation_teacher"
          filterable
          placeholder="助教老师"
        >
          <el-option
            :label="teacher.nickname + ' '+ teacher.phone"
            :value="teacher.user_id"
            :key="teacher.user_id"
            v-for="(teacher) in relationTeacher"
          >
            <span style="float:left">{{teacher.nickname}}</span>
            <span style="float:right">{{teacher.phone}}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="教室">
        <el-select v-model="class_info.classroom_name" filterable placeholder="教室编号">
          <el-option
            :label="classroom.value"
            :value="classroom.value"
            :key="classroom.value"
            v-for="(classroom) in searchData.classroom"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="开班人数" prop="class_number">
        <el-input-number v-model="class_info.class_number" :min="0"></el-input-number>
      </el-form-item>
      <el-form-item label="备注">
        <el-input type="textarea" v-model="class_info.class_remark"></el-input>
      </el-form-item>
      <div class="tips-bar">排课信息</div>
      <el-form-item label="单次扣除课时" v-if="class_info.attend_type / 1 === 2">
        <el-input-number
          :step="0.01"
          :min="0.00"
          :precision="2"
          controls-position="right"
          v-model="class_info.attend_times"
        ></el-input-number>
      </el-form-item>
      <el-form-item label="开始时间" prop="startDate">
        <el-date-picker
          @change="timeChange"
          v-model="datePickerData.timeRange[0]"
          class="date-picker-center"
          type="date"
        ></el-date-picker>
        <el-select
          v-if="hasEnd == '1'"
          class="template-item"
          v-model="dateTempIndex"
          placeholder="日期模板"
          filterable
          @change="dateTempChange"
        >
          <el-option
            :label="item.tpl_name"
            :value="index"
            :key="item.tpl_id"
            v-for="(item,index) in dateTempList"
          >
            <span style="float:left">{{item.tpl_name}}</span>
            <span style="float:right">{{item.start_date | formatToDate("Y-M-D")}} ~ {{item.end_date | formatToDate("Y-M-D")}}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="datePickerData.timeRange[0]" label="排班方式">
        <el-select style="width:200px" @change="hasEndChange" :disabled="isEdit" v-model="hasEnd">
          <el-option label="规则排班" value="0"></el-option>
          <el-option label="日历排课" value="1"></el-option>
        </el-select>
        <el-date-picker
          v-if="hasEnd === '1'"
          style="marginLeft:10px"
          class="date-picker-center"
          @change="timeChange"
          v-model="datePickerData.timeRange[1]"
          type="date"
        ></el-date-picker>
        <div class="tips-scheduling-wrap">
          <i class="hoo hoo-feedback_fill"></i>
          <span class="tips-scheduling">{{ tipsScheduling }}</span>
        </div>
      </el-form-item>
      <el-form-item v-if="datePickerData.timeRange[0]" label="上课时间" prop="dateData">
        <v-date-check
          ref="dateCheck"
          :hasWeek="true"
          hasTime
          :showAdd="true"
          :hasRange="false"
          :noDate="dateCheckStatus.noDate"
          @modelChange="dateChange"
          v-model="datePickerData"
          useTimeTemp
        ></v-date-check>
      </el-form-item>
    </el-form>

    <el-button slot="buttons" type="primary" @click="beforeOnSubmit">保存班级信息</el-button>
    <el-button slot="buttons" @click="cancle">取消</el-button>
  </v-form-wrap>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { creatClass, updateClass, classInfo, getTeacherList } from "@/api/class_control";
import { userList } from "@/api/school_control";
import { subjeckList, getCourseList } from "@/api/course_control";
import dateCheck from "@/components/date_check/index";
import formWrap from "@/components/pub_form_wrap";
import { getTemplateList } from "@/api/date_template";
export default {
  data() {
    let checkNumber = (rule, value, callback) => {
      let reg = /^([1-9]\d*|[0]{1,1})$/;
      let num = this.class_info.class_number;
      callback(reg.test(num) ? undefined : "请输入整数人数");
    };
    let checkStartDate = (rule, value, callback) => {
      let startTime = this.datePickerData.timeRange[0];
      // 预留开始时间 为空通过验证判断（待后台去除后台必填验证）
      // if (startTime === undefined || startTime === null || startTime === '') {
      //   callback();
      // } else {
      //   callback(startTime ? undefined : "请选择开始时间");
      // }
      callback(startTime ? undefined : "请选择开始时间");
    };
    let checkDate = (rule, value, callback) => {
      let { timeRange, listWeek, timeArr } = this.datePickerData;
      let startTime = this.datePickerData.timeRange[0];
      if (this.hasEnd === "1") {
        if (!timeRange[1]) {
          callback("请选择上课结束时间");
          return;
        } else if (timeRange[0] > timeRange[1]) {
          callback("结束时间不能小于开始时间");
          return;
        }
      }
      if (startTime !== undefined && startTime !== null && startTime !== '') {
        if (listWeek && listWeek.length !== 0) {
          for (let i = 0; i < listWeek.length; i++) {
            if (!timeArr) {
              callback(`请选择${this.$getWeekLabel(listWeek[i])}上课时间`);
              return;
            }
            let temp = timeArr.find(item => item.week / 1 === listWeek[i]);
            if (!temp) {
              callback(`请选择${this.$getWeekLabel(listWeek[i])}上课时间`);
              return;
            }
            let { start_time, end_time } = temp;
            if (start_time && end_time) {
              start_time = Date.parse(new Date("2018-01-01 " + start_time));
              end_time = Date.parse(new Date("2018-01-01 " + end_time));
              if (start_time > end_time) {
                callback(`${this.$getWeekLabel(temp.week)}的开始时间不能大于结束时间`);
                return;
              }
            } else {
              callback(`请选择${this.$getWeekLabel(temp.week)}上课时间`);
              return;
            }
          }
        } else {
          callback(`请先勾选左侧按钮，再选择上课时间`);
          return;
        }
      }
      callback();
    };
    return {
      class_id: "",
      typeList: this.$store.getters.getAttendType,
      class_info: {
        attend_type: 0,
        class_id: "",
        class_name: "",
        class_number: "",
        class_remark: "",
        classroom_name: "",
        recruit_status: "1",
        start_time: "",
        end_time: "",
        org_grade: "",
        teacher_id: "",
        course_time: 0,
        org_term: "",
        org_subject: "",
        chooseCourse: "",
        attend_times: 1,
        relation_teacher: [],
        course_id_list:[]
      },
      classInfoRules: {
        chooseCourse: [{ required: true, message: "请选择课程模板", trigger: "change" }],
        class_name: [{ required: true, message: "请填课程名称", trigger: "blur" }],
        class_number: [{ required: true, validator: checkNumber, trigger: ["blur", "change"] }],
        dateData: [{ required: true, validator: checkDate, trigger: ["click", "change"] }],
        teacher_id: [{ required: true, message: "请选择教师", trigger: "change" }],
        startDate: { required: true, validator: checkStartDate, trigger: ["change", "blur"] }
      },
      hasEnd: "0",
      datePickerData: {
        timeRange: [],
        date: [],
        weekArr: []
      },
      teacher_list: [],
      subject: [],
      term: [],
      grade: [],
      formLoading: false,
      isEdit: false,
      typeLabel: this.$store.getters.getAttendTypeLabel,
      dateTempList: [], // 日期模板列表
      dateTempIndex: "", // 日期模板选中index
      tipsScheduling: '没有固定结束日期, 每周按照规则自动生成课表',
      is_one_to_one: '',
      is_endTime: this.$route.query.is_endTime,
    };
  },
  created() {
    let query = this.$route.query;
    this.is_one_to_one = query.is_one_to_one;
    if (!!this.$route.query.class_id) { // 编辑班级
      this.class_id = this.$route.query.class_id;
      this.isEdit = true;
      this.getClassInfo();
    } else { // 新建班级
      let end_date = query.end_date;
      let dateData = {
        timeRange: [],
        date: [],
        weekArr: []
      };
      if (end_date && end_date / 1 !== 0) {
        dateData.timeRange = [query.start_date, query.end_date];
        dateData.date = query.select_day ? JSON.parse(query.select_day) : [];
      }
      this.datePickerData = dateData;
      Object.assign(this.class_info, {
        org_grade: query.grade,
        org_term: query.term,
        org_subject: query.subject,
        attend_type: query.attend_type
      });
      this.CourseList();
    }
    this.getTempList();
    this.getTeacherList();
    let str = `${this.isEdit ? "编辑" : "新增"}班级`;
    this.$store.dispatch("setTopTitle", {
      des: str,
      title: str
    });
  },
  components: {
    "v-date-check": dateCheck,
    "v-form-wrap": formWrap
  },
  methods: {
    handlleTempList(list) {
      if (list && this.class_info.course_id_list.length !== 0) {
        this.class_info.chooseCourse = list.findIndex((value, index, arr) => {
          return list[index].course_id === this.class_info.course_id_list[0]
        })
      }
    },
    teacherChange(val) {
      let list = this.class_info.relation_teacher.filter(i=>i !=val);
      this.class_info = Object.assign({},this.class_info,{relation_teacher:list})
    },
    dateTempChange(index) {
      let tempItem = this.dateTempList[index];
      this.range = [
        this.$getTimeStamp({ time: tempItem.start_date, returnType: "date" }),
        this.$getTimeStamp({ time: tempItem.end_date, returnType: "date" })
      ];
      this.hasEnd = "1";
      this.datePickerData = {
        timeRange: this.range,
        date: [],
        weekArr: []
      };
      this.$nextTick(() => {
        this.$refs.dateCheck.userTemplate({ type: "date", data: tempItem.date });
      });
    },
    getTempList() {
      getTemplateList({ tpl_type: 1, page: 1, size: 10000 }).then(res => {
        this.dateTempList = res.data.list;
      });
    },
    hasEndChange(val) {
      let timeRange = this.datePickerData.timeRange;
      let data = {
        timeRange: [timeRange[0], val / 1 === 1 ? timeRange[1] : ""],
        date: [],
        weekArr: []
      };
      this.datePickerData = data;
      this.$refs.form.clearValidate("dateData");
      if (val == 0) {
        this.tipsScheduling = "没有固定结束日期，每周按照规则自动生成课表；";
      } else {
        this.tipsScheduling = "在固定的时间范围内，勾选具体的上课日期；";
      }
    },
    timeChange(e) {
      let pickData = this.datePickerData;
      let { timeRange } = pickData;
      if (this.hasEnd == 1) {
        let _tempRange = [];
        if (timeRange[0]) {
          _tempRange[0] = this.$getTimeStamp(timeRange[0], 13);
        }
        if (timeRange[1]) {
          _tempRange[1] = this.$getTimeStamp(timeRange[1], 13);
        }
        this.datePickerData = {
          timeRange: _tempRange,
          date: [],
          weekArr: []
        };
      }
    },
    dateChange(e) {
      this.$refs.form.validateField("dateData");
    },
    classNameFocus() {
      let { class_name = "", org_term = "", org_grade = "", org_subject = "" } = this.class_info;
      if (class_name === "") {
        this.class_info.class_name = `${org_term}${org_grade}${org_subject}`;
      }
    },
    toCourseTemp() {
      this.$router.push({
        path: "/course/course_setting",
        query: {
          type: 1
        }
      });
    },
    /**
    * beforeOnSubmit
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/10/16
     */
    beforeOnSubmit () {
      if (this.class_info.chooseCourse !== undefined) {
        this.onSubmit()
      } else {
        this.$message.error('课程模板未选择，新建或编辑无法保存，请重新选择课程模板')
      }
    },
    
    // 注册方法
    onSubmit() {
      this.$refs.form
        .validate()
        .then(() => {
          // JSON.stringfy 和JSON.parse 会导致时间Date对象变为字符串
          let classInfo = Object.assign({}, this.class_info);
          classInfo.course_id_list = []
          classInfo.course_id_list.push(this.tempList[this.class_info.chooseCourse].course_id)
          let { timeRange, date, timeArr } = this.datePickerData;
          classInfo.start_time = this.$getTimeStamp(timeRange[0]);
          classInfo.end_time = this.hasEnd / 1 === 1 ? this.$getTimeStamp(timeRange[1]) : "0";
          classInfo.time_table = this.hasEnd / 1 === 1 ? JSON.stringify(date) : "[]";
          classInfo.week_list = JSON.stringify(timeArr);
          classInfo.relation_teacher = JSON.stringify(classInfo.relation_teacher);
          delete classInfo.org_id;
          classInfo.attend_times = classInfo.attend_type / 1 === 2 ? classInfo.attend_times : 1;
          classInfo.is_one_to_one = this.is_one_to_one;
          this.formLoading = true;
          return this.isEdit ? updateClass(classInfo) : creatClass(classInfo);
        })
        .then(res => {
          if (!res) return;
          this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
          if(this.isEdit) {
            this.$router.push({
              name: "class_detail",
              query: {
                class_id: this.class_id,
                is_endTime: this.is_endTime,
                is_one_to_one: this.is_one_to_one,
              }
            });
          } else {
            this.$router.push({
              path: "/course/class_control",
              query: {
                distinguish: this.is_one_to_one
              }
            });
          }
          this.formLoading = false;
        })
        .catch(e => {
          this.formLoading = false;
          this.$message.error(e === false ? "请填入必选项" : e);
        });
    },
    CourseList() {
      this.$store.dispatch("getCourseTempList", {
        attend_type: this.isEdit ? this.class_info.attend_type : ""
      });
      
    },
    selectCourse(index) {
      this.$refs.form.clearValidate();
      let courseItem = this.tempList[index];
      this.class_info.org_subject = courseItem.subject_name;
      this.class_info.org_grade = courseItem.grade;
      this.class_info.org_term = courseItem.course_term;
      this.class_info.attend_type = courseItem.attend_type / 1;
      let params = {};
      if (!courseItem.start_date || !courseItem.end_date) {
        if (!this.isEdit) this.hasEnd = "0";
        params.timeRange = [];
      } else {
        if (!this.isEdit) this.hasEnd = "1";
        params.timeRange = [
          this.$getTimeStamp(courseItem.start_date, 13),
          this.$getTimeStamp(courseItem.end_date, 13)
        ];
      }
      params.date = courseItem.time_table;
      this.datePickerData = Object.assign({}, this.datePickerData, params);
    },
    getClassInfo() {
      this.formLoading = true;
      classInfo({ class_id: this.class_id })
        .then(res => {
          let class_info = res.data;
          let { start_time, end_time } = class_info;
          start_time = this.$getTimeStamp(start_time, 13);
          let datePickerData = {
            timeArr: class_info.week_list,
            weekArr: class_info.week_list.map(i => i.week / 1)
          };
          if (end_time && end_time / 1 != 0) {
            end_time = this.$getTimeStamp(end_time, 13);
            Object.assign(datePickerData, {
              timeRange: [start_time, end_time],
              date: class_info.time_table
            });
            this.hasEnd = "1";
          } else {
            datePickerData.timeRange = [start_time, ""];
            this.hasEnd = "0";
          }
          // 一对一类型，自动创建的班级 默认显示日历排班
          if (this.is_one_to_one == 1) {
            this.hasEnd = this.is_one_to_one;
          }
          class_info.teacher_id = class_info.teacher_id == 0 ? "" : class_info.teacher_id;
          class_info.relation_teacher = this.$copyObject(class_info.relation_teacher_ids);
          this.datePickerData = datePickerData;
          class_info.attend_type = class_info.attend_type / 1;
          this.class_info = class_info;
          this.formLoading = false;
          this.is_one_to_one = class_info.is_one_to_one;
          this.CourseList();
        })
        .catch(error => {
          this.formLoading = false;
          this.$message.error(error);
        });
    },
    getTeacherList() {
      let obj = {
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          this.teacher_list = res.data.list.filter((val, index) => {
            return val.status / 1 === 1 || val.status / 1 === 2;
          });
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    cancle() {
      this.$router.push({
        path: "/course/class_control",
        query: {
          distinguish: this.is_one_to_one
        }
      });
    }
  },
  watch: {
    tempList(newVal, oldVal) {
      this.handlleTempList(newVal)
    }
  },
  computed: {
    relationTeacher() {
      if (this.teacher_list.length == 0) return [];
      return this.teacher_list.filter(i => i.user_id !== this.class_info.teacher_id);
    },
    relationTeacherDisabled() {
      return !this.class_info || !this.class_info.teacher_id;
    },
    ...mapState({
      courseTempList: state => state.course.courseTempList
    }),
    tempList() {
      let tempList = this.courseTempList.get(this.isEdit ? this.class_info.attend_type : "");
      let oneToone = this.is_one_to_one;
      let tempData = [];
      if (tempList && tempList.length !== 0){
        // 新建和编辑班级时 过滤班课和一对一的模板
        tempList.forEach(item => {
          if (oneToone == item.is_one_to_one) {
            if (item.is_open === '1') {
              tempData.push(item);
            }
          }
        });
        tempList = tempData;
      }
      this.handlleTempList(tempList)
      return tempList;
    },
    ...mapGetters({
      searchData: "common/getSearchData"
    }),
    dateCheckStatus() {
      let hasEnd = this.hasEnd === "1";
      return {
        noDate: hasEnd ? false : true,
        dateTemp: hasEnd ? true : false
      };
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.label-item
  border-radius: 50%;
  width: 16px;
  height: 16px;
  padding: 0 3px;
  background: #bbb;
  color: #fff;
.pub-form-wrap
  .tips-bar
    margin-left: 20px;
.time-list
  display: flex;
  flex-direction: column;
  .time-item
    width: 500px;
    display: flex;
    border: 1px solid #ececec;
    .time-label
      flex: 0 0 100px;
      border-right: 1px solid #ececec;
    .time-timepicker
      display: flex;
      .time-start, .time-end
        padding: 0 10px;
.flex-bar
  .time-picker
    min-width: 300px;
  .select-item
    margin-left: 10px;
.course-name-left
  float: left;
.course-name-right
  float: right;
  color: #8492a6;
  font-size: 13px;
.setting-wrap
  color: #8690ac
  strong
    margin-left: 15px;
    font-weight: 600;
  span
    margin-left: 5px;
.tips-scheduling-wrap
  display: inline-block;
  color: #8690ac
  i
    margin: 0 5px 0 10px;

</style>
