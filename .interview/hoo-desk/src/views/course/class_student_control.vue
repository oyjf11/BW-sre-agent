<template>
  <el-dialog :visible.sync="dialogShow" class="class_stu_control" @close="close">
    <template slot="title">
      <span style="font-size: 20px">{{classInfo.class_name}}</span>
    </template>
    <el-form v-loading="dialogLoading">
      <el-form-item label="已排学生">
        <div class="stu-list" v-show="chooseStuList.length !==0">
          <el-button
            class="student_btn"
            @click="delStudent(item,index,0)"
            v-for="(item,index) in chooseStuList"
            :key="index"
          >
            {{item.student_name}}
            <i class="fa fa-minus" style="color: #7B9ED4;"></i>
          </el-button>
          <el-button @click="delAll" type="primary">
            删除全部
            <i class="fa fa-minus" style="color: #fff;"></i>
          </el-button>
        </div>
        <span v-show="chooseStuList.length ==0">暂无学生</span>
      </el-form-item>
      <div class="add-stu-box">
        <div class="label">添加学生</div>
        <div class="value-wrap">
          <el-select
            v-model="chooseStu"
            multiple
            style="width:500px"
            :filterable="true"
            default-first-option
            placeholder="搜索姓名可快速找到学生"
          >
            <el-option
              v-for="(item) in studentList"
              :label="item.student_name"
              :value="item.order_course_id"
              :key="item.order_course_id"
              style="display: flex"
            >
              <span style="flex:2;padding:0 5px">{{typeLabel[item.attend_type]}}</span>
              <span style="flex:3;padding:0 5px">{{item.student_name}}</span>
              <span style="flex:3;padding:0 5px">{{item.course_term}}</span>
              <span style="flex:2;padding:0 5px">{{item.grade}}</span>
              <span style="flex:2;padding:0 5px">{{item.subject_name}}</span>
              <span style="flex:2;padding:0 5px">{{item.surplus_hours}}</span>
            </el-option>
          </el-select>
          <el-button @click="toAdd">添加</el-button>
          <div class="check-bar">
            <el-checkbox @change="stuStatusChange" v-model="stuStatus">快速换班</el-checkbox>
            <p class="tips-check"><i class="hoo hoo-feedback_fill"></i>勾选后可查找到已排班的学员并快速换班至本班级</p>
          </div>
        </div>
      </div>
      <el-form-item>
        <el-button
          type="text"
          v-if="closedStuList.length > 0"
          @click="showCloseStu = !showCloseStu"
        >查看课时已耗完或已过期的学员（{{ closedStuList.length }}）名</el-button>
        <!-- {{ showCloseStu ? '收起' : '展开' }} -->
      </el-form-item>
      <el-form-item>
        <div class="stu-list" v-show="closedStuList.length && showCloseStu">
          <el-button
            class="student_btn"
            v-for="(item,index) in closedStuList"
            @click="delStudent(item,index,1)"
            :key="index"
          >
            {{item.student_name}}
            <i class="fa fa-minus" style="color: #7B9ED4;"></i>
          </el-button>
        </div>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>



<script>
import { classInfo } from "@/api/class_control";
import { studentList, addStudent } from "@/api/class_control";
import { delStu } from "@/api/student_control";
export default {
  props: {
    id: null,
    dialog: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    typeLabel: function() {
      return this.$store.getters.getAttendTypeLabel;
    }
  },
  data() {
    return {
      showCloseStu: false, // 展开已结课的学生列表
      dialogShow: false,
      classInfo: {},
      dialogLoading: false,
      studentList: [],
      chooseStu: [],
      closedStuList: [], // 已经结课的学生
      chooseStuList: [], // 选中的学生
      stuStatus: false, // false未排班  true 已排班
      hasStuList: [], //本班既有学生
      stuListMap: new Map([
        [false, { status: false, list: [] }],
        [true, { status: false, list: [] }]
      ])
    };
  },
  methods: {
    stuStatusChange(val) {
      this.stuStatus = val;
      let item = this.stuListMap.get(this.stuStatus);
      if (!item.status) {
        this.getStuList();
      } else {
        this.studentList = item.list;
      }
    },
    // 获取班级信息和学生列表
    getClassAndStuList() {
      this.dialogLoading = true;
      this.stuListMap.set(false, { status: false, list: [] });
      this.stuListMap.set(true, { status: false, list: [] });
      classInfo({ class_id: this.id })
        .then(res => {
          console.log(res, "获取班级详情");
          this.classInfo = res.data;
          this.chooseStuList = res.data.student_list;
          this.closedStuList = res.data.closed_list;
          this.hasStuList = [...res.data.student_list, ...res.data.closed_list];
          let type = [2, 3].includes(this.classInfo.attend_type / 1)
            ? "2,3"
            : this.classInfo.attend_type;
          let obj = {
            page: 1,
            count: 10000,
            has_class: this.stuStatus ? 2 : 1,
            subject_name: this.classInfo.org_subject,
            attend_type: type
          };
          return studentList(obj);
        })
        .then(res => {
          let list = res.data.list;
          // 已排班学生列表的去除本班学生
          if (this.stuStatus) {
            list = list.filter(
              i =>
                !this.hasStuList.some(
                  _i => _i.stu_id === i.stu_id && _i.edu_stu_id === i.edu_stu_id
                )
            );
          }
          this.stuListMap.set(this.stuStatus, { status: true, list: list });
          this.studentList = list;
          this.dialogLoading = false;
        })
        .catch(e => {
          this.dialogLoading = false;
          console.log(e);
        });
    },
    toAdd() {
      if (this.chooseStu.length == 0) {
        this.$message.error("请选择学生后再添加");
        return;
      }
      let obj = {
        class_id: this.classInfo.class_id,
        student_list: JSON.stringify(this.chooseStu)
      };
      this.dialogLoading = true;
      addStudent(obj)
        .then(res => {
          this.$message.success("添加学生成功");
          this.chooseStu = [];
          this.$emit("refresh");
          this.getClassAndStuList();
        })
        .catch(e => {
          console.log(e);
          this.dialogLoading = false;
          this.$message.error(e);
        });
    },
    getStuList() {
      this.dialogLoading = true;
      let type = [2, 3].includes(this.classInfo.attend_type / 1)
        ? "2,3"
        : this.classInfo.attend_type;
      let obj = {
        page: 1,
        count: 10000,
        has_class: this.stuStatus ? 2 : 1,
        subject_name: this.classInfo.org_subject,
        attend_type: type,
        class_id:this.classInfo.class_id
      };
      studentList(obj)
        .then(res => {
          let list = res.data.list;
          // 已排班学生列表的去除本班学生
          if (this.stuStatus) {
            list = list.filter(
              i =>
                !this.hasStuList.some(
                  _i => _i.stu_id === i.stu_id && _i.edu_stu_id === i.edu_stu_id
                )
            );
          }
          this.stuListMap.set(this.stuStatus, { status: true, list: list });
          this.studentList = list;
          this.dialogLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.dialogLoading = false;
        });
    },
    delAll() {
      this.$confirm("此操作将删除该班级的所有学生, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let ids = this.chooseStuList.map(val => {
            return val.edu_stu_id;
          });
          let obj = {
            student_ids: JSON.stringify(ids)
          };
          return delStu(obj);
        })
        .then(res => {
          this.$message.success("删除成功");
          this.getClassAndStuList();
          this.$emit("refresh");
        })
        .catch(e => {
          if (e != "cancel") {
            console.log("e", e);
            this.$message.error(e);
          }
        });
    },
    delStudent(item, index, type) {
      // type 0 已排班学生  1 已结课学生
      this.$confirm("此操作将移除该学生, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            student_ids: JSON.stringify([item.edu_stu_id])
          };
          return delStu(obj);
        })
        .then(res => {
          if (res) {
            if (type === 1) {
              this.closedStuList.splice(index, 1);
            } else {
              this.chooseStuList.splice(index, 1);
            }
            // 剔除hasStuList的该学生
            this.hasStuList = this.hasStuList.filter(i => i.edu_stu_id !== item.edu_stu_id);
            this.$message.success("删除成功");
            this.getStuList();
            this.$emit("refresh");
          }
        })
        .catch(e => {
          if (e != "cancel") {
            console.log("e", e);
            this.$message.error(e);
          }
        });
    },
    close() {
      this.chooseStu = [];
      this.$emit("onClose", false);
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.stuStatus = false;
        this.getClassAndStuList();
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.stu-list
  .student_btn
    margin-right: 10px;
  .el-button
    margin-bottom: 10px;
.add-stu-box
  display: flex;
  .label
    padding-right: 12px;
    flex: 0 0 auto;
    line-height: 36px;
    font-size: 14px;
    color: #606266;
    text-align: right;
  .value-wrap
    flex: 1;
    .check-bar
      margin: 10px 0;
.tips-check
  display: inline-block;
  color: #8690ac;
  i
    margin: 0 5px 0 15px;
</style>

