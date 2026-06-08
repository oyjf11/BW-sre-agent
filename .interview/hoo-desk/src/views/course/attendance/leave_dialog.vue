<template>
  <el-dialog title="添加请假" width="500px" :visible.sync="dialogShow" @close="close">
    <el-form
      :model="formData"
      :rules="formRules"
      ref="leaveForm"
      class="pub-form"
      label-width="120px"
    >
      <el-form-item label="姓名" prop="student">
        <el-select
          v-model="formData.student"
          @change="getTimeList"
          filterable
          remote
          value-key="class_id"
          :disabled="!!formData.student"
          placeholder="请输入学员姓名或手机号"
          :remote-method="studentRemote"
          :loading="leaveData.loading"
        >
          <el-option
            v-for="(item,index) in leaveData.list"
            :key="index"
            :value="item"
            :label="item.showLabel"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="请假日期" prop="leaveTime">
        <el-select
          v-model="formData.leaveTime"
          @change="filterTimeList"
          filterable
          :loading="leaveData.timeLoading"
          :disabled="!!!formData.student"
          placeholder="选择日期"
        >
          <el-option
            v-for="(item,index) in leaveData.timeList"
            :key="index"
            :value="item"
            :label="item.showLabel"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="原因" prop="remark">
        <el-input placeholder="请输入请假原因" type="textarea" v-model="formData.remark"></el-input>
      </el-form-item>
    </el-form>
    <div slot="footer" class="dialog-btn-bar">
      <el-button @click="close">取消</el-button>
      <el-button class="submit-btn" @click="reset">重置</el-button>
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
  createLeaves
} from "@/api/course_control";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    info: Object
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
      formRules: {
        student: {
          required: true,
          message: "请选择学生",
          trigger: ["blur", "change"]
        },
        leaveTime: {
          required: false,
          message: "请选择日期",
          trigger: ["blur", "change"]
        }
      },
      formData: {
        student: "",
        leaveTime: "",
        remark: "",
        order_course_id: "",
        attendance_date: "",
        attend_type: '', // 1: 按期; 2: 按次; 3: 按月;
        start_time: '',
        end_time: '',
      },
      dialogShow: false,
      leaveData: {
        list: [],
        loading: false,
        timeList: [],
        timeLoading: false
      },
      edu_stu_id: '',
      att_id: '',
      class_id: ''
    };
  },
  methods: {
    close() {
      this.dialogShow = false;
      this.reset();
      this.$emit("onClose");
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
      this.leaveData.list = [];
      this.leaveData.timeList = [];
    },
    studentRemote(query) {
      if (query === "") {
        this.leaveData.list = [];
        return;
      }
      this.leaveData.loading = true;
      getStudentList({ search: query })
        .then(res => {
          console.log('%cres.data.list','font-size:40px;color:pink;',res.data.list)
          this.leaveData.loading = false;
          this.leaveData.list = this.studentLabel(res.data.list);
        })
        .catch(e => {
          console.log("error", e);
          this.leaveData.loading = false;
        });
    },
    studentLabel(list) {
      list.forEach(item => {
        let str = item.student_name + " - ";
        try {
          str += item.contacts[0].phone + " - ";
        } catch (e) {
          str += "无 - ";
        }
        str += item.class_name ? item.class_name + " - " : "无 - ";
        str += item.teacher_name ? item.teacher_name : "无";
        item.showLabel = str;
      });
      return list;
    },
    filterTimeList(item){
      this.formData.leaveTime = item.att_id;
      this.att_id = item.att_id;
      this.formData.order_course_id = item.order_course_id;
      this.formData.attendance_date = item.attendance_date;
      this.formData.attend_type = item.attend_type;
      this.formData.start_time = item.start_time;
      this.formData.end_time = item.end_time;
      this.formData.leaveTime = item.showLabel;
    },
    getTimeList(item) {
      console.log('%citem','font-size:40px;color:pink;',item)
      this.leaveData.timeList = this.timeLable(item.time_table);
      this.class_id = item.class_id;
      this.edu_stu_id = item.edu_stu_id;
      this.formData.student = item.showLabel
      // this.
      // let params = {
      //   class_id: item.class_id
      // };
      // this.leaveData.timeLoading = true;
      // getTimeList(params)
      //   .then(res => {
      //     // console.log("班级上课时间表", res);
      //     this.leaveData.timeList = this.timeLable(res.data);
      //     this.leaveData.timeLoading = false;
      //   })
      //   .catch(e => {
      //     console.log(e);
      //     this.leaveData.timeLoading = false;
      //     this.$message.error("获取时间失败");
      //   });
    },
    timeLable(list) {
      // 在att_id为空的情况下，select框会变得不能选择，所以在为空的情况下把attendance_date的值赋给att_id，让页面可以选择，
      // 保存的时候如果是attendance_date则不添加到字段中
      list.forEach(item => {
        item.showLabel = item.attendance_date + " " + item.start_time + "-" + item.end_time;
        if (item.att_id == '' || item.att_id == null) {
          item.att_id = item.attendance_date
        }
      });
      return list;
    },
    save() {
      this.$refs.leaveForm
        .validate()
        .then(res => {
          let data = {}
          // 大于7位则是前端做处理后的假att_id，这个att_id本来就是空，所以重新赋值""
          if (this.att_id.length > 9) {
            data = {
              class_id: this.class_id,
              student_id: this.edu_stu_id,
              att_id: ""
            };
          } else {
            data = {
              class_id: this.class_id,
              student_id: this.edu_stu_id,
              att_id: this.att_id
            };
          }
          data.order_course_id = this.formData.order_course_id;
          data.attendance_date = this.formData.attendance_date;
          data.attend_type = this.formData.attend_type;
          data.start_time = this.formData.start_time;
          data.end_time = this.formData.end_time;
          return createLeaves(data);
        })
        .then(res => {
          if (res) {
            this.$message.success("添加请假成功");
            this.reset();
            this.dialogShow = false;
            this.$emit("onRefresh");
          }
          console.log(res);
        })
        .catch(e => {
          if (e === false) {
            this.$message.error("请输入必填项");
          } else {
            this.$message.error(e);
          }
        });
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
      }
    }
  }
};
</script>
