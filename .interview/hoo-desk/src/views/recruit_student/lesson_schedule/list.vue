<template>
  <v-table-wrap
    :page="page"
    :total="count"
    showSearch
    placeholder="教师、学员搜索"
    @onSearch="filterChange($event,'search')"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <template slot="searchItems">
      <v-mutex-check-bar
        label="科目"
        :checkList="searchData.subject"
        @onChange="filterChange($event,'subject')"
      ></v-mutex-check-bar>
      <v-mutex-check-bar
        label="学期"
        :checkList="searchData.term"
        @onChange="filterChange($event,'term')"
      ></v-mutex-check-bar>
      <v-time-bar
        :all="false"
        :time="datetime"
        :timeList="timeLabelList"
        @onChange="filterChange($event,'datetime')"
      ></v-time-bar>
      <div class="btn-bar" style="padding-left:0">
        <div class="filter-label">校区</div>
        <div>
          <el-select
            @change="selectChange"
            style="width:300px"
            v-model="filter_ids"
            placeholder="请选择"
            multiple
          >
            <el-option
              v-for="item in org_list"
              :key="item.org_id"
              :label="item.org_name"
              :value="item.org_id"
            ></el-option>
          </el-select>
        </div>
      </div>
    </template>
    <template slot="table_title">课消表</template>
    <el-button slot="table_btns" type="primary" @click="exportList">导出列表</el-button>
    <div slot="table_count">共消耗金额{{total_consume_amount}}元，共消耗课时{{total_used_times}}课时</div>
    <el-table slot="table" v-loading="tableLoading" class="pub-table" :data="listData">
      <el-table-column prop="org_name" label="校区"></el-table-column>
      <el-table-column prop="teacher_name" label="教师名称">
        <template slot-scope="scope">{{scope.row.teacher_name ? scope.row.teacher_name :"-"}}</template>
      </el-table-column>
      <el-table-column prop="student_name" label="学员名称"></el-table-column>
      <el-table-column prop="course_name" label="课程名称"></el-table-column>
      <el-table-column prop="times" label="购买课时"></el-table-column>
      <el-table-column label="已消耗课时">
        <template slot-scope="scope">
          <el-button type="text" @click="toDetails(scope.row)">{{scope.row.used_times}}</el-button>
        </template>
      </el-table-column>
      <el-table-column label="已消耗金额">
        <template slot-scope="scope">
          <el-button type="text" @click="toDetails(scope.row)">{{scope.row.consume_amount}}</el-button>
        </template>
      </el-table-column>
    </el-table>
  </v-table-wrap>
</template>


<script>
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import { AttrList } from "@/api/operations_center";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import { getLessonSchedule, exportLessonSchedule } from "@/api/student_control";
import { mapGetters } from "vuex";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      datetime: [],
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      tableLoading: false,
      listData: [],
      subject: null,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      filter_ids: [],
      term: null,
      total_consume_amount: '',
      total_used_times: '',
    };
  },
  created() {
    let start_date = new Date(new Date().setDate(1)).setHours(0, 0, 0, 0);
    let end_date = new Date().setHours(23, 59, 59, 0);
    this.datetime = [start_date / 1000, end_date / 1000];
  },
  activated() {
    // 新版不请求
    if(!this.isNewType)this.getList();
  },
  methods: {
    exportList() {
      let obj = {
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        subject: this.subject,
        term: this.term,
        filter_ids: this.filter_ids.join(",")
      };
      exportLessonSchedule(obj)
        .then(res => {
          console.log("res", res);
          this.$downLoad(res.data);
          this.$message.success("导出成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error("导出失败");
        });
    },
    selectChange() {
      this.getList();
    },
    getList() {
      this.tableLoading = true;
      let obj = {
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        page: this.page,
        size: this.size,
        subject: this.subject,
        term: this.term,
        filter_ids: this.filter_ids.join(",")
      };
      getLessonSchedule(obj)
        .then(res => {
          console.log(res);
          this.listData = res.data.list;
          this.total_consume_amount = res.data.total_consume_amount
          this.total_used_times = res.data.total_used_times
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          this.tableLoading = false;
        });
    },
    toDetails(item) {
      this.$router.push({
        name: "lesson_schedule_student",
        query: {
          order_course_id: item.order_course_id,
          teacher_id: item.teacher_id,
          start_date: this.datetime[0],
          end_date: this.datetime[1]
        }
      });
    },
    filterChange(e, type) {
      if (type !== "page") this.page = 1;
      this[type] = e;
      this.getList();
    }
  },
  components: {
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData",
      org_list: "common/getownOrgList",
      isNewType: "common/getSystemType"
    })
  }
};
</script>
