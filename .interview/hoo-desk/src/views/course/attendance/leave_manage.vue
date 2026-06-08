// 请假管理
<template>
  <div class>
    <div class="ask-for-leave">
      <v-leave @submit="createSubmit"></v-leave>
    </div>
    <v-table-wrap
      :total="count"
      :page="page"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <div slot="table_count">共 {{count}} 条, 人数 {{studentNum}}, 课时 {{lessionNum}}</div>
      <el-table slot="table" class="pub-table" :data="listData" v-loading="listLoading">
        <el-table-column label="校区" prop="org_name"></el-table-column>
        <el-table-column label="姓名" prop="student_name"></el-table-column>
        <el-table-column label="班级" prop="class_name"></el-table-column>
        <el-table-column label="请假日期">
          <template slot-scope="scope">
            <p>{{scope.row.attendance_date}}</p>
            <p>{{scope.row.start_time}} - {{scope.row.end_time}}</p>
          </template>
        </el-table-column>
        <el-table-column label="课时" prop="hours"></el-table-column>
        <el-table-column label="补课">
          <template slot-scope="scope">
            <div v-if="scope.row.new_attendance_date">
              <p>{{scope.row.new_attendance_date}} {{scope.row.new_start_time}} - {{scope.row.new_end_time}}</p>
              <p>{{scope.row.new_class_name}} ({{scope.row.new_teacher_name}})</p>
            </div>
            <p v-else>暂无安排</p>
          </template>
        </el-table-column>
        <el-table-column label="原因" prop="remark">
          <template slot-scope="scope">
            <p v-if="scope.row.remark">{{scope.row.remark}}</p>
            <p v-else>无</p>
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">修改</el-button>
            <el-button type="text" @click="toDel(scope.row)">撤销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>>
    <el-dialog @close="dialogClose" :visible.sync="dialogShow">
      <v-leave :bindInfo="bindInfo" @submit="editSubmit"></v-leave>
    </el-dialog>
  </div>
</template>

<script>
import {
  createLeaves,
  getLeaveList,
  updateLeave,
  delLeave,
  getTimeList,
  getStudentList,
  getTeacherList,
  getLeaveDetails
} from "@/api/course_control";
import leaveForm from "./leave_form";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      listData: [],
      listLoading: false,
      size: 10,
      page: 1,
      count: 0,
      studentNum: 0,
      lessionNum: 0,
      dialogShow: false,
      bindInfo: null
    };
  },
  components: {
    "v-leave": leaveForm,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      getLeaveList({ page: this.page, size: this.size })
        .then(res => {
          console.log("res", res);
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.studentNum = res.data.total_user / 1;
          this.lessionNum = res.data.total_hour / 1;
        })
        .catch(e => {
          console.log(e, "error");
        });
    },
    createSubmit(data) {
      createLeaves(data)
        .then(res => {
          console.log("res", res);
          this.getList();
          this.$message.success("请假提交成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    editSubmit(data) {
      let params = Object.assign(data, { att_id: this.bindInfo.att_id });
      createLeaves(data)
        .then(res => {
          console.log("res", res);
          this.dialogShow = false;
          this.getList();
          this.$message.success("请假修改成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    toEdit(item) {
      this.dialogShow = true;
      this.bindInfo = item;
    },
    dialogClose() {
      this.bindInfo = null;
    },
    toDel(item) {
      this.$confirm("此操作将撤销该请假, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delLeave({ att_id: item.att_id });
        })
        .then(res => {
          this.getList();
          this.$message.success("撤销该请假成功");
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    }
  }
};
</script>


<style lang="stylus" scoped>
.ask-for-leave
  padding-top: 20px;
  width: 700px;
</style>

