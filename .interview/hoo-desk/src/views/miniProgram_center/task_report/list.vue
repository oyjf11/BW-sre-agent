<template>
  <div>
    <div class="pub-filter-box">
      <v-search-bar placeholder="请输入学生名称"
                    @onSearch='toSearch'></v-search-bar>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">任务报告</div>
      </div>
      <el-table class='pub-table'
                :data='listData'
                v-loading="tableLoading"
                v-if='type == 0'>
        <el-table-column label='任务名称'
                         prop='comment_title'></el-table-column>
        <el-table-column label='子任务数量'
                         prop='child_mission_number'></el-table-column>
        <el-table-column label='总人数'
                         prop='send_number'></el-table-column>
        <el-table-column label='完成人数'
                         prop='complete_number'></el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='toDetails(scope.row)'>查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-table class='pub-table'
                :data='listData'
                v-loading="tableLoading"
                v-else>
        <el-table-column label='学生姓名'
                         prop='student_name'></el-table-column>
        <el-table-column label='班级'
                         prop='comment_title'></el-table-column>
        <el-table-column label='任务数量'
                         prop='child_mission_number'></el-table-column>
        <el-table-column label='已完成'
                         prop='complete_number'></el-table-column>
        <el-table-column label='综合评分'
                         prop='average_rating'></el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='toDetails(scope.row)'>查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pagination">
      <span class="demonstration"></span>
      <el-pagination @current-change="pageChange"
                     :current-page="page"
                     :page-size="10"
                     layout="total, prev, pager, next, jumper"
                     :total="count">
      </el-pagination>
    </div>
  </div>
</template>




<script>
import { getReportList } from "@/api/miniProgram_center";
import searchBar from "@/components/top_box/search_bar";
export default {
  data() {
    return {
      type: "1",
      tableLoading: false,
      listData: [],
      page: 1,
      size: 10,
      count: 0,
      search: ""
    };
  },
  activated() {
    if (this.$route.query.type) {
      this.type = this.$route.query.type;
    }
    this.$store.dispatch("setTopTitle", {
      des: "任务报告",
      title: "任务报告"
    });
    this.getList();
  },
    components: {
    "v-search-bar": searchBar
  },
  methods: {
    toSearch(val) {
      this.search = val;
      this.page = 1;
      this.getList();
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    listChange(val) {
      this.$router.replace({
        name: "taks_report",
        query: { type: val }
      });
    },
    toDetails(item) {
      let id = this.type == 0 ? item.day_mission_id : item.student_id;
      this.$router.push({
        name: "task_report_info",
        query: { type: this.type, id: id, org_id: item.org_id }
      });
    },
    getList() {
      this.tableLoading = true;
      let obj = {
        page: this.page,
        count: this.size,
        search: this.search
      };
      obj.postType = this.type;
      getReportList(obj)
        .then(res => {
          console.log(res, "获取列表返回");
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    }
  }
};
</script>
