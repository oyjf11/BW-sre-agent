<template>
  <div>
    <el-form :model="formData"
             :rules="formRules"
             ref='leaveForm'
             class='pub-form'
             label-width="120px">
      <el-form-item label="姓名"
                    prop="student">
        <el-select v-model="formData.student"
                   @change="getTimeList($event,1)"
                   filterable
                   remote
                   value-key="class_id"
                   :disabled="!!formData.student"
                   placeholder="请输入学员姓名或手机号"
                   :remote-method="studentRemote"
                   :loading="leaveData.loading">
          <el-option v-for="(item,index) in leaveData.list"
                     :key="index"
                     :value="item"
                     :label="item.showLabel">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="请假日期"
                    prop="leaveTime">
        <el-select v-model="formData.leaveTime"
                   filterable
                   :loading="leaveData.timeLoading"
                   :disabled="!!!formData.student"
                   placeholder="选择日期">
          <el-option v-for="(item,index) in leaveData.timeList"
                     :key="index"
                     :value="item.timetable_id"
                     :label="item.showLabel">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="补课"
                    prop="lession">
        <el-select :disabled="!!!formData.student"
                   v-model="formData.lession"
                   filterable
                   remote
                   clearable
                   value-key="class_id"
                   @change="getTimeList($event,2)"
                   placeholder="请输入教师名称或班级名称"
                   :remote-method="lessionRemote"
                   :loading="lessionData.loading">
          <el-option :key="index"
                     :label="item.showLabel"
                     :value='item'
                     v-for="(item,index) in lessionData.list">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="formData.lession"
                    label="补课日期"
                    prop="lessionTime">
        <el-select v-model="formData.lessionTime"
                   filterable
                   :loading="lessionData.timeLoading"
                   placeholder="选择日期">
          <el-option v-for="(item,index) in lessionData.timeList"
                     :key="index"
                     :value="item.timetable_id"
                     :label="item.showLabel">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="原因"
                    prop="remark">
        <el-input placeholder="请输入请假原因"
                  type="textarea"
                  v-model="formData.remark"></el-input>
      </el-form-item>
    </el-form>
    <div class="btn-bar">
      <el-button class="submit-btn"
                 type="primary"
                 @click='submit'>提交</el-button>
      <el-button class="submit-btn"
                 @click='reset'>重置</el-button>
    </div>
  </div>
</template>


<script>
import {
  getTimeList,
  getStudentList,
  getTeacherList,
  getLeaveDetails
} from "@/api/course_control";
export default {
  props: ["bindInfo"],
  data() {
    var checkLessionTime = (rule, value, callback) => {
      if (this.formData.lession) {
        if (value) {
          callback();
        } else {
          callback("请选择补课日期");
        }
      } else {
        callback();
      }
    };
    return {
      formRules: {
        student: {
          required: true,
          message: "请选择学生",
          trigger: ["blur", "change"]
        },
        leaveTime: {
          required: true,
          message: "请选择请假日期",
          trigger: ["blur", "change"]
        },
        lessionTime: {
          required: true,
          validator: checkLessionTime,
          trigger: ["blur", "change"]
        }
      },
      formData: {
        student: null,
        leaveTime: null,
        lession: null,
        lessionTime: null,
        remark: ""
      },
      leaveData: {
        list: [],
        loading: false,
        timeList: [],
        timeLoading: false
      },
      lessionData: {
        list: [],
        loading: false,
        timeList: [],
        timeLoading: false
      },
      isEdit: false
    };
  },
  created() {
    if (this.bindInfo) {
      this.isEdit = true;
      this.getInfo();
    }
  },
  watch: {
    bindInfo() {
      if (this.bindInfo === null) {
        return;
      }
      this.getInfo();
      this.$refs.leaveForm.resetFields();
    }
  },
  methods: {
    getInfo() {
      getLeaveDetails({ att_id: this.bindInfo.att_id })
        .then(res => {
          console.log("res", res);
          if (!res.data) {
            return;
          }
          this.leaveData.list = [
            {
              edu_stu_id: res.data.stu_id,
              showLabel: this.bindInfo.student_name,
              class_id: res.data.class_id
            }
          ];
          // 用settimeout 解决select框初始化Bug
          setTimeout(() => {
            this.formData.student = {
              edu_stu_id: res.data.stu_id,
              showLabel: this.bindInfo.student_name,
              class_id: res.data.class_id
            };
          }, 0);
          if (res.data.new_class_name && res.data.new_teacher_name) {
            this.formData.lession =
              res.data.new_class_name + "-" + res.data.new_teacher_name;
            this.lessionData.timeList = this.timeLable(res.data.new_timetable);
            this.formData.lessionTime = res.data.new_timetable_id;
          }
          this.leaveData.timeList = this.timeLable(res.data.timetable);
          this.formData.leaveTime = res.data.timetable_id;
          this.formData.remark = this.bindInfo.remark;
        })
        .catch(e => {
          console.log(e, "error");
          this.$message.error("加载数据失败");
          // this.leaveData.list = [
          //   {
          //     edu_stu_id: res.data.stu_id,
          //     showLabel: this.bindInfo.student_name,
          //     class_id: res.data.class_id
          //   }
          // ];
          // this.formData.student = {
          //   edu_stu_id: res.data.stu_id,
          //   showLabel: this.bindInfo.student_name,
          //   class_id: res.data.class_id
          // };
        });
    },
    studentRemote(query) {
      if (query === "") {
        this.leaveData.list = [];
        return;
      }
      this.leaveData.loading = true;
      getStudentList({ search: query })
        .then(res => {
          this.leaveData.loading = false;
          this.leaveData.list = this.studentLabel(res.data.list);
        })
        .catch(e => {
          console.log("error", e);
          this.leaveData.loading = false;
        });
    },
    lessionRemote(query) {
      if (query === "") {
        this.lessionData.list = [];
        return;
      }
      this.lessionData.loading = true;
      getTeacherList({ search: query, size: 1000 })
        .then(res => {
          this.lessionData.loading = false;
          this.lessionData.list = this.teacherLabel(res.data.list);
          console.log("教师列表", res);
        })
        .catch(e => {
          console.log(e);
          this.lessionData.loading = false;
        });
    },
    getTimeList(item, type) {
      console.log(item,type);
      if (!item) {
        return;
      }
      let str = type === 1 ? "leaveData" : "lessionData";
      let params = {
        class_id: item.class_id
      };
      if (type === 2) {
        this.formData.lessionTime = null;
      }
      this[str].timeLoading = true;
      getTimeList(params)
        .then(res => {
          // console.log("班级上课时间表", res);
          this[str].timeList = this.timeLable(res.data);
          this[str].timeLoading = false;
        })
        .catch(e => {
          console.log(e);
          this[str].timeLoading = false;
          this.$message.error("获取时间失败");
        });
    },
    submit() {
      this.$refs.leaveForm.validate(valid => {
        if (valid) {
          let data = {
            student_id: this.formData.student.edu_stu_id,
            timetable_id: this.formData.leaveTime,
            remedy_id: this.formData.lession ?  this.formData.lessionTime : "",
            remark: this.formData.remark
          };
          this.$emit("submit", data);
        }
      });
    },
    reset() {
      if (this.isEdit) {
        this.formData = Object.assign(
          { student: this.formData.student },
          {
            leaveTime: null,
            lession: null,
            lessionTime: null,
            remark: ""
          }
        );
        this.$refs.leaveForm.clearValidate();
      } else {
        this.$refs.leaveForm.resetFields();
      }
      this.$emit("reset");
    },
    timeLable(list) {
      list.forEach(item => {
        item.showLabel =
          item.class_date + " " + item.start_time + "-" + item.end_time;
      });
      return list;
    },
    studentLabel(list) {
      list.forEach(item => {
        let str = item.student_name + " - ";
        try {
          let contact = JSON.parse(item.contacts);
          str += contact[0].phone + " - ";
        } catch (e) {
          str += "无 - ";
        }
        str += item.class_name ? item.class_name + " - " : "无 - ";
        str += item.teacher_name ? item.teacher_name : "无";
        item.showLabel = str;
      });
      return list;
    },
    teacherLabel(list) {
      list.forEach(item => {
        item.showLabel = item.teacher_name + " - " + item.class_name;
      });
      return list;
    }
  }
};
</script>

<style lang="stylus" scoped>
.pub-form
  margin-top: 0;
.btn-bar
  display: flex;
  .submit-btn
    width: 120px;
    margin-left: 140px;
</style>
