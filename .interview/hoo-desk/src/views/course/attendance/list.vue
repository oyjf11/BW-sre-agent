// 出勤报表
<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <v-time-bar
        :all="false"
        slot="searchItems"
        :time="datetime"
        :timeList="timeLabelList"
        :handleFunc="timeHandleFunc"
        :timePickerOption="timePickerOption"
        @onChange="filterChange($event,'datetime')"
      ></v-time-bar>
      <template slot="table_title">出勤列表</template>
      <div slot="table_count">
        <span>总出勤率：{{attendanceValid}}/{{attendanceCount}} &nbsp; 出勤率:{{attendanceValid | calcPercent(attendanceCount)}}</span>
        <span>每天晚上凌晨01:00更新数据</span>
      </div>
      <el-table slot="table" :data="listData" v-loading="listLoading" class="pub-table">
        <el-table-column label="校区" prop="org_name"></el-table-column>
        <el-table-column label="时间" prop="month"></el-table-column>
        <el-table-column label="出勤情况">
          <template slot-scope="scope">{{scope.row.attendance}}/{{scope.row.count}}</template>
        </el-table-column>
        <el-table-column label="出勤率">
          <template slot-scope="scope">{{scope.row.ratio}} %</template>
        </el-table-column>
        <el-table-column label="缺勤人次" prop="absence"></el-table-column>
        <el-table-column label="请假人次" prop="leave"></el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toDetails(scope.row)">查看详细</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import { getOrgAttendanceList } from "@/api/course_control";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      datetime: ["", ""],
      listData: [],
      listLoading: false,
      page: 1,
      size: 10,
      count: 0,
      attendanceValid: 0,
      attendanceCount: 0,
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
          let endTimeDays = new Date(endTimeYears, endTimeMonth + 1, 0).getDate();
          let end_time = new Date(endTimeYears, endTimeMonth, endTimeDays).setHours(23, 59, 59, 0);
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
          let end_time = new Date(year, month, monthDays).setHours(23, 59, 59, 0);
          return [start_time, end_time];
        }
      }
    };
  },
  created() {
    let nowDay = new Date();
    let year = nowDay.getFullYear();
    let month = nowDay.getMonth();
    let monthDays = new Date(year, month + 1, 0).getDate();
    let start_time = new Date(year, month, 1).getTime();
    let end_time = new Date(new Date(year, month, monthDays)).setHours(23, 59, 59, 0);
    this.datetime = [start_time / 1000, end_time / 1000];
  },
  activated(){
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  components: {
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      let obj = {
        page: this.page,
        size: this.size,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      };
      this.listLoading = true;
      getOrgAttendanceList(obj)
        .then(res => {
          console.log(res);
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.attendanceValid = res.data.attendance_valid;
          this.attendanceCount = res.data.attendance_count;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    toDetails(item) {
      let time = item.month.split("-");
      let year = time[0];
      let month = time[1];
      let start_time = new Date(item.month).setHours(0, 0, 0, 0);
      let days = new Date(year, month, 0).getDate();
      let end_time = new Date(start_time).setDate(days);
      end_time = new Date(end_time).setHours(23, 59, 59, 0);
      let params = {
        org_id: item.org_id,
        start_time: start_time / 1000,
        end_time: end_time / 1000
      };
      this.$router.push({
        name: "attendance_details",
        query: params
      });
    }
  },
  computed:{
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
  },
};
</script>

<style lang="stylus" scoped>
</style>

