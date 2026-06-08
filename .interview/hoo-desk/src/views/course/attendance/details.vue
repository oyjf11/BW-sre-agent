// 出勤报表-详情
<template>
  <div>
    <div class="pub-filter-box">
      <v-time-bar
        :all="false"
        :time="datetime"
        :timeList="timeLabelList"
        :handleFunc="timeHandleFunc"
        :timePickerOption="timePickerOption"
        @onChange="timeChange"
      ></v-time-bar>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">出勤列表</div>
        <div class="count">
          <span>总出勤率：{{attendanceValid}}/{{attendanceCount}} &nbsp; 出勤率:{{attendanceValid | calcPercent(attendanceCount)}}</span>
          <span>每天晚上凌晨01:00更新数据</span>
        </div>
      </div>
      <el-table
        class="pub-table"
        :data="listData"
        ref="tableList"
        @expand-change="tableRowExpand"
        @row-click="tableRowClick"
        v-loading="listLoading"
      >
        <el-table-column type="expand">
          <template slot-scope="scope">
            <ul class="date-list" v-if="scope.row.dateList">
              <li class="date-item" v-for="(item,index) in scope.row.dateList" :key="index">
                <div class="date-wrap" @click="showDialogFunc(scope.row,index)">
                  <div class="date-title">{{index + 1}}</div>
                  <div
                    v-if="item !== undefined"
                    :class="['date-content',item.isAfter ?'':'text-light']"
                  >{{item.attendance}}/{{item.count}}</div>
                  <div v-else>无课</div>
                </div>
              </li>
            </ul>
            <div v-if="!scope.row.dateList">暂无数据</div>
          </template>
        </el-table-column>
        <el-table-column label="校区" prop="org_name"></el-table-column>
        <el-table-column label="科目" prop="org_subject"></el-table-column>
        <el-table-column label="时间" prop="month"></el-table-column>
        <el-table-column label="教师" prop="teacher_name"></el-table-column>
        <el-table-column label="班级" prop="class_name"></el-table-column>
        <el-table-column label="出勤情况">
          <template slot-scope="scope">{{scope.row.attendance}} / {{scope.row.count}}</template>
        </el-table-column>
        <el-table-column label="出勤率">
          <template slot-scope="scope">{{scope.row.ratio}} %</template>
        </el-table-column>
        <el-table-column label="缺勤人次" prop="absence"></el-table-column>
        <el-table-column label="请假人次" prop="leave"></el-table-column>
      </el-table>
      <div class="pagination">
        <span class="demonstration"></span>
        <el-pagination
          @current-change="pageChange"
          :current-page="page"
          :page-size="size"
          layout="total, prev, pager, next, jumper"
          :total="count"
        ></el-pagination>
      </div>
    </div>
    <v-attendance @onClose="closeDialog" :classId='bindClassId'  :classAttendTimes="bindAttendTimes" :id="bindId" :dialogType="2" :dialog="showDialog"></v-attendance>
  </div>
</template>

<script>
import AttendanceDialog from "./attendance_dialog";
import timeBar from "@/components/top_box/time_bar";
import {
  getClassAttendanceList,
  getClassAttendanceInfoByMonth
} from "@/api/course_control";
export default {
  data() {
    return {
      timeLabelList: [
        { label: "最近1月", value: "1" },
        { label: "最近3月", value: "3" },
        { label: "最近6月", value: "6" }
      ],
      timePickerOption: {
        format: "yyyy-MM",
        func: function(val) {
          let start_time = new Date(val[0].setDate(1)).setHours(0, 0, 0, 0);
          let endTimeYears = val[1].getFullYear();
          let endTimeMonth = val[1].getMonth();
          let endTimeDays = new Date(
            endTimeYears,
            endTimeMonth + 1,
            0
          ).getDate();
          let end_time = new Date(
            endTimeYears,
            endTimeMonth,
            endTimeDays
          ).setHours(23, 59, 59, 0);
          return [start_time, end_time];
        }
      },
      timeHandleFunc: {
        enable: true,
        func: function(val) {
          let nowDay = new Date();
          let year = nowDay.getFullYear();
          let month = nowDay.getMonth();
          let monthDays = new Date(year, month + 1, 0).getDate();
          let start_time = new Date(year, month, 1);
          start_time = start_time.setMonth(start_time.getMonth() - (val - 1));
          let end_time = new Date(year, month, monthDays).setHours(
            23,
            59,
            59,
            0
          );
          return [start_time, end_time];
        }
      },
      listData: [],
      listLoading: false,
      showDialog: false,
      dateList: [],
      bindInfo: {},
      org_id: 0,
      page: 1,
      size: 10,
      count: 0,
      datetime: ["", ""],
      attendanceCount: 0,
      attendanceValid: 0,
      dateInit: false,
      dateExpandInit: false,
      bindId: null,
      bindAttendTimes:1,
      bindClassId:""
    };
  },
  components: {
    "v-attendance": AttendanceDialog,
    "v-time-bar": timeBar
  },
  created() {
    this.org_id = this.$route.query.org_id;
    if (this.$route.query.start_time) {
      this.datetime = [
        this.$route.query.start_time,
        this.$route.query.end_time
      ];
    }
    this.$store.dispatch("setTopTitle", {
      des: "出勤报表",
      title: "出勤报表"
    });
    this.getList();
  },
  methods: {
    timeChange(val) {
      this.datetime = val;
      this.page = 1;
      this.getList();
    },
    getList() {
      let obj = { page: this.page, size: this.size, org_id: this.org_id };
      if (this.datetime[0]) {
        obj.start_time = this.datetime[0];
        obj.end_time = this.datetime[1];
      }
      this.listLoading = true;
      getClassAttendanceList(obj)
        .then(res => {
          console.log(res);
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.attendanceCount = res.data.attendance_count;
          this.attendanceValid = res.data.attendance_valid;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    showDialogFunc(item, index) {
      let dateInfo = item.dateList[index];
      if (!dateInfo || dateInfo.isAfter) {
        return;
      }
      this.bindAttendTimes = dateInfo.attend_times;
      this.bindId = dateInfo.timetable_id;
      this.bindClassId = item.class_id;
      this.showDialog = true;
    },
    closeDialog(refresh) {
      this.showDialog = false;
      if (refresh) {
        this.getList();
      }
    },
    tableRowExpand(row) {
      if (this.dateInit) {
        this.dateInit = false;
        return;
      }
      if (this.dateExpandInit) {
        this.dateExpandInit = false;
        this.$refs.tableList.toggleRowExpansion(row);
        return;
      }
      if (row.dateList) {
        return;
      }
      this.getDateList(row)
        .then(res => {
          this.dateExpandInit = true;
          this.$refs.tableList.toggleRowExpansion(row);
        })
        .catch(e => {
          this.$message.error(e);
          console.log(e);
        });
    },
    tableRowClick(row, event, column) {
      this.dateInit = true;
      if (row.dateList) {
        this.$refs.tableList.toggleRowExpansion(row);
        return;
      }
      this.getDateList(row)
        .then(res => {
          this.$refs.tableList.toggleRowExpansion(row);
        })
        .catch(e => {
          this.$message.error(e);
          console.log(e);
        });
    },
    getDateList(row) {
      return new Promise((resolve, reject) => {
        let obj = {
          class_id: row.class_id,
          month: row.month
        };
        getClassAttendanceInfoByMonth(obj)
          .then(res => {
            console.log(res, "获取成功");
            let time = row.month.split("-");
            let year = time[0];
            let month = time[1];
            let list = Array.from({
              length: new Date(year, month, 0).getDate()
            });
            res.data.list.forEach(item => {
              let day = item.day.split("-")[2] - 1;
              item.isAfter =
                new Date(item.day).setHours(0, 0, 0, 0) -
                  new Date().setHours(0, 0, 0, 0) >
                0
                  ? true
                  : false;
              list[day] = item;
            });
            row.dateList = list;
            resolve();
          })
          .catch(e => {
            reject(e);
          });
      });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  }
};
</script>

<style lang="stylus" scoped>
.date-list
  display: flex;
  width: 100%;
  flex-wrap: wrap;
  padding-bottom: 20px;
  .date-item
    flex: 0 0 auto;
    width: 8.3%;
    text-align: center;
    margin-bottom: 20px;
    .date-wrap
      cursor: pointer;
      display: inline-block;
      width: auto;
      margin: 0 auto;
      .date-title
        font-weight: 600;
        margin-bottom: 10px;
      .text-light
        color: #03a9fe;
      &:hover
        opacity: 0.8;
</style>
