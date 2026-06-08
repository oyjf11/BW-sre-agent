// 考勤管理
<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      showSearch
      placeholder="请输入教师或班级名称"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="openDialog">临时排课</el-button>
      <template slot="searchItems">
        <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          :handleFunc="timeHandleFunc"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar>
        <v-mutex-check-bar
          label="科目"
          :checkList="searchData.subject"
          @onChange="filterChange($event,'subject')"
        ></v-mutex-check-bar>
      </template>
      <template slot="table_title">考勤列表</template>
      <el-button @click="exportList" slot="table_btns" type="primary">导出课程表</el-button>
      <el-table slot="table" v-loading="listLoading" :data="listData" class="pub-table">
        <!-- <el-table-column label="校区" prop="org_name"></el-table-column> -->
        <el-table-column label="科目" prop="org_subject"></el-table-column>
        <el-table-column label="教师" prop="teacher_name" width="120"></el-table-column>
        <el-table-column label="班级" prop="class_name" width="120"></el-table-column>
        <el-table-column label="时间" prop="class_date" width="120"></el-table-column>
        <el-table-column label="学员" width="700">
          <template slot-scope="scope">
            <el-tooltip placement="top" popper-class="stu-content">
              <div slot="content">{{scope.row.student_list | stuFormate}}</div>
              <span class="stu-text">{{scope.row.student_list | stuFormate}}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="授课课时">
          <template slot-scope="scope">{{scope.row.attend_times ? scope.row.attend_times : "-" }}</template>
        </el-table-column>
        <el-table-column label="出勤状况">
          <template slot-scope="scope">{{scope.row.attendance}} / {{scope.row.student_count}}</template>
        </el-table-column>
        <el-table-column label="出勤率">
          <template
            slot-scope="scope"
          >{{scope.row.attendance | calcPercent(scope.row.student_count)}}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" class-name="table-btn-column">
          <template slot-scope="scope">
            <!-- 出勤大于1个，显示取消一键考勤 -->
            <el-button
              :disabled="scope.row.isAfter"
              type="text"
              v-if="scope.row.student_count / 1 !== 0"
              @click="setAllAttendance(scope.row)"
            >{{scope.row.attendance > 0 ? "取消一键考勤" :'一键考勤'}}</el-button>
            <el-button type="text" @click="showDialogFunc(scope.row, 2, 0)">操作</el-button>
            <el-button
              type="text"
              v-if="scope.row.is_temporary == 1 && scope.row.attendance == 0"
              @click="delAttendance(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>

    <v-attendance
      @onClose="closeDialog"
      :classAttendTimes="bindAttendTimes"
      :id="bindId"
      :classId="bindClassId"
      :dialog="showDialog"
      :status="bindStatus"
      :timetableId="timetable_id"
      :items="items"
    ></v-attendance>
    <el-dialog title="临时排课" width="500px" :visible.sync="dialogShow" @close="close">
      <el-form :model="tempAttendance" label-width="100px">
        <el-form-item label="班级">
          <el-select
            v-model="tempAttendance.class_id"
            filterable
            remote
            clearable
            value-key="class_id"
            placeholder="请输入教师名称或班级名称"
            :remote-method="classRemote"
            :loading="classList.loading"
          >
            <el-option
              v-for="(item,index) in classList.list"
              :key="index"
              :value="item.class_id"
              :label="item.showLabel"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期">
          <el-date-picker
            v-model="tempAttendance.class_date"
            class="date-picker-center"
            value-format="yyyy-MM-dd"
            type="date"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="上课时间">
          <el-time-picker
            is-range
            format="HH:mm"
            v-model="tempAttendance.timeRange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            placeholder="选择时间范围"
          ></el-time-picker>
        </el-form-item>
      </el-form>
      <el-button type="primary" slot="footer" @click="save">保存</el-button>
      <el-button slot="footer" @click="close">取消</el-button>
    </el-dialog>
  </div>
</template>

<script>
import {
  curriculumList,
  setAllStudentAttendance,
  exportList,
  addTempAttendance,
  delTempAttendance
} from "@/api/course_control";
import { ClassList } from "@/api/class_control";
import AttendanceDialog from "./attendance_dialog";
import timeBar from "@/components/top_box/time_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      tempAttendance: {
        class_id: "",
        class_date: "",
        timeRange: null
      },
      classList: {
        loading: false,
        list: []
      },
      item: { // 临时排课 点击保存时赋值
        class_date: '',
        start_time: '',
        end_time: ''
      },
      dialogShow: false,
      page: 1,
      size: 10,
      count: 0,
      timeBtnValue: "day",
      datetime: ["", ""],
      listData: [],
      listLoading: false,
      showDialog: false,
      bindId: "",
      bindAttendTimes: 1,
      bindClassId: "",
      subject: "",
      search: "",
      timeLabelList: [
        { label: "日", value: "day" },
        { label: "周", value: "week" },
        { label: "月", value: "month" }
      ],
      timeHandleFunc: {
        enable: true,
        func: function(val) {
          let startDate = new Date().setHours(0, 0, 0, 0);
          let endDate = new Date().setHours(23, 59, 59, 0);
          if (val === "week") {
            endDate = new Date(endDate);
            endDate = endDate.setDate(endDate.getDate() + 7);
          } else if (val === "month") {
            endDate = new Date(endDate);
            endDate = endDate.setMonth(endDate.getMonth() + 1);
          }
          return [startDate, endDate];
        }
      },
      bindStatus: 0,
      items: [],
      timetable_id:null
    };
  },
  created() {
    this.datetime = [
      new Date().setHours(0, 0, 0, 0) / 1000,
      new Date().setHours(23, 59, 59, 0) / 1000
    ];
  },
  activated() {
    // 新版不请求
    if (!this.isNewType) this.getList();
  },
  components: {
    "v-attendance": AttendanceDialog,
    "v-time-bar": timeBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    openDialog(){
      this.dialogShow = true;
      this.tempAttendance.class_date = this.$formatToDate(new Date(),"Y-M-D")
    },
    delAttendance(item) {
      this.$confirm("是否删除此考勤记录", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delTempAttendance({ id: item.id });
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.getList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") this.$message.error(e);
        });
    },
    save() {
      console.log(this.tempAttendance);

      if (!this.tempAttendance.class_id) {
        this.$message.error("请选择班级");
        return;
      }
      if (!this.tempAttendance.class_date) {
        this.$message.error("请选择上课日期");
        return;
      }
      if (!this.tempAttendance.timeRange) {
        this.$message.error("请选择上课时间");
        return;
      }
      let obj = {
        class_id: this.tempAttendance.class_id,
        class_date: this.tempAttendance.class_date
      };
      let timeRange = this.tempAttendance.timeRange;
      if (timeRange) {
        obj.start_time = this.$formatToDate(timeRange[0], "h:m");
        obj.end_time = this.$formatToDate(timeRange[1], "h:m");
      }
      addTempAttendance(obj)
        .then(res => {
          console.log("res0713", res);
          this.timetable_id = res.data.timetable_id
          console.log('%cthis.timetable_idccccccccccc','font-size:40px;color:pink;',this.timetable_id)
          this.getList();
          this.$message.success("添加成功");
          this.showDialogFunc(res.data,'',1);
          this.item.class_date = this.tempAttendance.class_date;
          this.item.start_time = obj.start_time;
          this.item.end_time = obj.end_time;
          this.close();
        })
        .catch(e => {
          console.log("e");
          this.$message.error(e);
        });
    },
    close() {
      this.tempAttendance = {
        class_id: "",
        class_date: "",
        start_time: "",
        end_time: ""
      };
      this.dialogShow = false;
    },
    classRemote(query) {
      if (query === "") {
        this.classList.list = [];
        return;
      }
      this.classList.loading = true;
      ClassList({ search: query, size: 1000 })
        .then(res => {
          console.log("教师列表", res);
          this.classList.loading = false;
          this.classList.list = res.data.list.map(i => {
            i.showLabel = `${i.teacher_name} - ${i.class_name}`;
            return i;
          });
        })
        .catch(e => {
          console.log(e);
          this.classList.loading = false;
        });
    },
    exportList() {
      let obj = {
        search: this.search,
        org_subject: this.subject,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      };
      exportList(obj)
        .then(res => {
          this.$downLoad(res.data);
        })
        .catch(e => {
          console.log(e);
          this.$message.error("导出失败");
        });
    },
    getList() {
      this.listLoading = true;
      let obj = {
        search: this.search,
        page: this.page,
        size: this.size,
        org_subject: this.subject,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      };
      curriculumList(obj)
        .then(res => {
          console.log(res, "课程表");
          this.count = res.data.count / 1;
          let list = res.data.list;
          let nowTime = new Date().setHours(0, 0, 0, 0);
          list.forEach(item => {
            let compareTime = new Date(item.class_date).setHours(0, 0, 0, 0);
            item.isAfter = compareTime - nowTime > 0 ? true : false;
          });
          this.listData = list;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      if (type === "subject") {
        let value = val.length > 0 ? val.split(",") : "";
        value = JSON.stringify(value);
        this[type] = value;
      } else {
        this[type] = val;
      }
      this.getList();
    },
    showDialogFunc(item, status, judge) {
      this.showDialog = true;
      this.bindAttendTimes = item.attend_times;
      this.bindId = item.timetable_id;
      if (judge == 1) { // 临时插班保存后进入 获取自临时插班弹窗选择的班级的class_id
        this.bindClassId = this.tempAttendance.class_id;
        this.items = this.item;
      } else { // 列表操作按钮进入 获取自当前行的class_id
        this.bindClassId = item.class_id;
        this.items = item;
      }
      console.log('%citems','font-size:40px;color:pink;',item)
      this.timetable_id = item.timetable_id
      this.bindStatus = status;
    },
    closeDialog(status) {
      this.showDialog = false;
      this.bindAttendTimes = 0;
      if (status) this.getList();
    },
    setAllAttendance(item) {
      // 出勤大于1个，取消一键考勤
      let is_duty = item.attendance > 0 ? 0 : 1;
      setAllStudentAttendance({ timetable_id: item.id, is_duty, attend_times: item.default_times })
        .then(res => {
          console.log(res);
          this.$message.success("一键考勤成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData",
      isNewType: "common/getSystemType"
    })
  },
  filters: {
    stuFormate(arr) {
      let tempArr = Array.from({ length: arr.length }).map((val, index) => arr[index].student_name);
      return tempArr.join("、");
    }
  }
};
</script>

<style scoped lang="stylus">
</style>
