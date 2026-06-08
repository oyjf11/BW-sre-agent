<template>
  <v-table-wrap 
    :page='page'
    :total="count"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <v-time-bar
      :all="false"
      slot="searchItems"
      :time="datetime"
      :timeList="timeLabelList"
      @onChange="filterChange($event,'datetime')"
    ></v-time-bar>
    <span slot="table_title">课消列表</span>
    <el-table slot="table" type='primary' v-loading="tableLoading" class="pub-table" :data="listData">
      <el-table-column prop="teacher_name" label="教师名称">
        <template slot-scope='scope'>
          {{scope.row.teacher_name ? scope.row.teacher_name :"-"}}
        </template>
      </el-table-column>
      <el-table-column prop="student_name" label="学员名称">
        <template slot-scope='scope'>
          {{scope.row.student_name ? scope.row.student_name :"-"}}
        </template>
      </el-table-column>
      <el-table-column prop="class_name" label="班级名称">
        <template slot-scope='scope'>
          {{scope.row.class_name ? scope.row.class_name :"-"}}
        </template>
      </el-table-column>
      <el-table-column prop="attendance_date" label="考勤日期">
        <template
          slot-scope="scope"
        >{{scope.row.attendance_date}} {{scope.row.start_time}}-{{scope.row.end_time}}</template>
      </el-table-column>
      <el-table-column label="授课课时" prop="attend_times"></el-table-column>
      <el-table-column label="课程单价" prop="price"></el-table-column>
      <el-table-column label="已消耗金额" prop="consume_amount"></el-table-column>
      <el-table-column label="备注" prop='remark'></el-table-column>
    </el-table>
  </v-table-wrap>
</template>


<script>
import { getLessonScheduleDetails } from "@/api/student_control";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      tableLoading: false,
      listData: [],
      page: 1,
      size: 10,
      count: 0,
      datetime: [],
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      teacher_id: '',
    };
  },
  created() {
    let query = this.$route.query;
    this.teacher_id = this.$route.query.teacher_id;
    let start_date = new Date(new Date().setDate(1)).setHours(0, 0, 0, 0);
    let end_date = new Date().setHours(23, 59, 59, 0);
    if (this.teacher_id != '') {
      this.datetime = [query.start_date ? query.start_date : start_date / 1000,query.end_date ? query.end_date: end_date / 1000];
    }
    this.getList();
  },
  components: {
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(e, type) {
      if (type !== "page") this.page = 1;
      this[type] = e;
      this.getList();
    },
    getList() {
      let obj = {};
      if (this.teacher_id != '') {
        obj = {
          order_course_id: this.$route.query.order_course_id,
          teacher_id: this.$route.query.teacher_id,
          page: this.page,
          size: this.size,
          start_date: this.datetime[0],
          end_date: this.datetime[1],
        }
      } else {
        obj = {
          order_course_id: this.$route.query.order_course_id,
          page: this.page,
          size: this.size,
          start_date: this.datetime[0],
          end_date: this.datetime[1],
        } 
      }
      getLessonScheduleDetails(obj)
        .then(res => {
          console.log('%clistData','font-size:40px;color:pink;',res.data.list)
          this.listData = res.data.list;
          this.count = res.data.count / 1;
        })
        .catch(e => {
          this.$message.error(e);
        });
    }
  }
};
</script>
