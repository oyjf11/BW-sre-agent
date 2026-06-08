<template>
  <div>
    <div class="pub-table-wrap">
      <el-table :data='listData'
                @sort-change='sortChange'
                v-loading='listLoading'
                class='pub-table'>
        <el-table-column label='学生姓名'
                         prop="student_name"></el-table-column>
        <el-table-column label="班级"
                         prop='class_name'></el-table-column>
        <el-table-column label="考试时间"
                         prop='test_date'>
          <template slot-scope="scope">
            {{scope.row.test_date | formatToDate("Y-M-D")}}
          </template>
        </el-table-column>
        <el-table-column label="考试名称"
                         prop='test_name'></el-table-column>
        <el-table-column label="科目">
          <template slot-scope='scope'>
            <template v-if="scope.row.org_subject">{{scope.row.org_subject}}</template>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <el-table-column label="分数/满分"
                         sortable="custom"
                         prop='score'>
          <template slot-scope='scope'>
            {{scope.row.score}} / {{scope.row.total_score}}
          </template>
        </el-table-column>
        <el-table-column label="平均分">
          <template slot-scope="scope">
            {{Number(scope.row.avg_score).toFixed(2)}}
          </template>
        </el-table-column>
        <el-table-column label="排名/全班"
                         sortable="custom"
                         prop='rank'>
          <template slot-scope='scope'>
            {{scope.row.rank}}/{{scope.row.full_class}}
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <span class="demonstration"></span>
        <el-pagination @current-change="pageChange"
                       :current-page="page"
                       :page-size="size"
                       layout="total, prev, pager, next, jumper"
                       :total="count">
        </el-pagination>
      </div>
    </div>
  </div>
</template>


<script>
import { getUnitTestStu } from "@/api/statistical";
export default {
  data() {
    return {
      student_name: "",
      org_subject: "",
      org_id: 1,
      page: 1,
      count: 0,
      size: 10,
      listData: [],
      listLoading: false,
      order_by: ""
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      title: "入门考统计-详情",
      des: "入门考统计-详情"
    });
    this.student_name = this.$route.query.student_name;
    this.org_subject = this.$route.query.org_subject
      ? this.$route.query.org_subject
      : "";
    this.org_id = this.$route.query.org_id;
    this.getList();
  },
  methods: {
    sortChange(data) {
      switch (data.prop) {
        case "score":
          this.order_by =
            data.order == "ascending" ? "score_asc" : "score_desc";
          break;
        case "rank":
          this.order_by = data.order == "ascending" ? "rank_asc" : "rank_desc";
          break;
        default:
          this.order_by = "";
      }
      this.page = 1;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getUnitTestStu({
        page: this.page,
        count: this.size,
        org_id: this.org_id,
        student_name: this.student_name,
        org_subject: this.org_subject,
        order_by: this.order_by
      })
        .then(res => {
          console.log(res, "返回");
          this.listLoading = false;
          this.listData = res.data.list;
          this.count = Number(res.data.total);
        })
        .catch(e => {
          this.listLoading = false;
          console.log(e);
        });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  }
};
</script>
