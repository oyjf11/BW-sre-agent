<template>
  <el-dialog :title="showTitle" width="500px" :visible.sync="dialogShow" @close="close">
    <el-form
      :model="formData"
      :rules="formRules"
      ref="leaveForm"
      class="pub-form"
      label-width="120px"
    >
      <el-form-item label="补课日期" prop="date">
        <el-date-picker v-model="formData.date" type="datetime" placeholder="选择日期时间" align="right"></el-date-picker>
      </el-form-item>
      <el-form-item label="补课班级" prop="classInfo">
        <el-select
          v-model="formData.classInfo"
          filterable
          remote
          value-key="class_id"
          placeholder="请输入教师名称或班级名称"
          :remote-method="classRemote"
          :loading="classList.loading"
        >
          <el-option
            v-for="(item,index) in classList.list"
            :key="index"
            :value="item"
            :label="item.showLabel"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="扣除课时" v-if="is_byOrder == true">
        <el-input type="Number" v-model="formData.class" @input="classChange(formData.class)"></el-input>
      </el-form-item>
      <el-form-item label="" v-if="is_byOrder == true">
          <div class="text-wrap">
            <p>当前学员剩余课时: <span class="blue-text">{{remaining_hours}}</span> 课时</p>
            <p>确认{{this.studentInfo.length !== 0 ? '补课' :'无需补课'}}后, 将会扣除该学员 <span class="blue-text">{{formData.class == '' ? 0 : formData.class}}</span> 课时,</p>
            <p v-show="class_tips" class="red-text"><i>*</i> 学员剩余课时不足</p>
          </div>
        </el-form-item>
    </el-form>
    <div class="dialog-btn-bar" slot="footer">
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </div>
  </el-dialog>
</template>


<script>
import {
  getTimeList,
  getStudentList,
  getTeacherList,
  getLeaveDetails,
  setAdjusst,
  getUserCourseTime
} from "@/api/course_control";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    is_byOrder: {
      type: Boolean,
      default: false
    },
    info: Array,
    adjustIsArr: Boolean
  },
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
      remaining_hours: 0,
      class_tips: false,
      formRules: {
        date: {
          required: true,
          message: "请选择时间",
          trigger: ["blur", "change"]
        },
        classInfo: {
          required: true,
          message: "请选择班级",
          trigger: ["blur", "change"]
        }
      },
      formData: {
        date: "",
        classInfo: "",
        class: ""
      },
      dialogShow: false,
      classList: {
        list: [],
        loading: false
      },
      studentInfo: []
    };
  },
  computed: {
    showTitle() {
      if (this.adjustIsArr) {
        return "批量补课";
      } else if (this.studentInfo.length !== 0) {
        let { class_name, student_name, teacher_name } = this.studentInfo[0];
        // return `${student_name} - ${class_name} - ${teacher_name}`;
        return "补课"
      } else {
        return "";
      }
    }
  },
  methods: {
    save() {
      this.$refs.leaveForm
        .validate()
        .then(res => {
          let att_idArr =[];
          let edu_stu_idArr = [];
          this.studentInfo.forEach(i=>{
            att_idArr.push(i.att_id);
            edu_stu_idArr.push(i.edu_stu_id);
          })
          let att_ids = att_idArr.join(",");
          let edu_stu_ids = edu_stu_idArr.join(",");
          // is_remedy 补课
          let { classInfo, date } = this.formData;
          let year = date.getFullYear();
          let month = date.getMonth() + 1;
          let day = date.getDate();
          let hours = date.getHours();
          let minutes = date.getMinutes();
          month = month < 10 ? "0" + month : month;
          day = day < 10 ? "0" + day : day;
          hours = hours < 10 ? "0" + hours : hours;
          minutes = minutes < 10 ? "0" + minutes : minutes;
          let params = {
            remedy_date: `${year}-${month}-${day}`,
            remedy_start_time: `${hours}:${minutes}`,
            att_ids,
            edu_stu_ids,
            is_remedy: 2,
            remedy_class_id: classInfo.class_id
          };
          if (this.is_byOrder == true) {
            params.attend_times = this.formData.class;
            if (this.formData.class == '') {
              this.$message.error("请输入扣除课时");
              return;
            }else if (this.class_tips) {
              this.$message.error("学员剩余课时不足");
              return;
            }
            return setAdjusst(params);
          } else {
            return setAdjusst(params);
          }
        })
        .then(res => {
          if (res) {
            this.dialogShow = false;
            this.$message.success("补课成功");
            this.$emit("onRefresh");
          }
          console.log(res);
        })
        .catch(e => {
          console.log("e",e);
          if (e === false) {
            this.$message.error("请输入必填项");
          } else {
            this.$message.error(e);
          }
        });
    },
    close() {
      this.dialogShow = false;
      this.$refs.leaveForm.resetFields();
      this.$emit("onClose");
    },
    classRemote(query) {
      if (query === "") {
        this.classList.list = [];
        return;
      }
      this.classList.loading = true;
      getTeacherList({ search: query, size: 1000 })
        .then(res => {
          console.log("教师列表", res);
          this.classList.loading = false;
          this.classList.list = this.teacherLabel(res.data.list);
        })
        .catch(e => {
          console.log(e);
          this.classList.loading = false;
        });
    },
    teacherLabel(list) {
      list.forEach(item => {
        item.showLabel = item.teacher_name + " - " + item.class_name;
      });
      return list;
    },
    /**
    * 获取剩余课时
    * getRemainingHours
    * @param  Boolean     {att_id}
     * Created by preference on 2019/09/24
     */
    getRemainingHours (item) {
      getUserCourseTime({att_id: item[0].att_id})
        .then(res => {
          this.remaining_hours = res.data.residue_time;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    /**
    * 课时
    * classChange
    * @param  Number     {value}
     * Created by preference on 2019/09/24
     */
    classChange (val) {
      if (val > this.remaining_hours) { // 输入扣除的课时 大于 剩余课时 则显示提示信息
        this.class_tips = true;
      } else {
        this.class_tips = false;
      }
    },
  },
  created() {

  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.studentInfo = this.$copyObject(this.info);
        this.getRemainingHours(this.info);
        this.formData.class=""
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.text-wrap
  line-height 20px
</style>
