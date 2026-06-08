 <template>
  <div>
    <div class="pub-filter-box">
      <div class="btn-bar">

      </div>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <span class='student-name'>{{studentName}}</span> 综合评分：{{starNum}}
      </div>
      <el-table v-loading='tableLoading'
                class='pub-table'
                :data='listData'>
        <el-table-column label='任务'
                         prop='comment_title'></el-table-column>
        <el-table-column label='星级'
                         prop='star'>
        </el-table-column>
        <el-table-column label='完成时间'>
          <template slot-scope="scope">
            {{scope.row.update_time | formatToDate}}
          </template>
        </el-table-column>
        <el-table-column label='描述'
                         prop='content'></el-table-column>
        <el-table-column label='子任务'>
          <template slot-scope="scope">
            <p v-for="(item,index) in scope.row.child_mission"
               :key='index'>
              {{item.name}}
            </p>
          </template>
        </el-table-column>
        <el-table-column label='星级评分'>
          <template slot-scope="scope">
            <p v-for="(item,index) in scope.row.child_mission"
               :key='index'>
              {{item.star}}
            </p>
          </template>
        </el-table-column>
      </el-table>
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
  </div>
</template>


<script>
import { getReportInfo } from "@/api/miniProgram_center";
export default {
  data() {
    return {
      type: null,
      org_id: null,
      id: null,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      listData: [],
      studentName: "学生名字",
      starNum: 0,
      tableLoading: false
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      title: "任务报告-详情",
      des: "任务报告"
    });
    let params = this.$route.query;
    this.type = params.type;
    this.org_id = params.org_id;
    this.id = params.id;
    console.log(params);
    this.getList();
  },
  methods: {
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    getList() {
      let obj = {
        search: this.search,
        count: this.size,
        page: this.page,
        postType: this.type
      };
      if (this.type == 0) {
        obj.mission_id = this.id;
      } else {
        obj.student_id = this.id;
      }
      this.tableLoading = true;
      getReportInfo(obj)
        .then(res => {
          console.log("详情返回", res);
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.studentName = res.data.student_name;
          this.starNum = res.data.average_rating;
          this.listData.forEach(item => {
            let star = 0;
            item.child_mission.forEach(subItem => {
              star += Number(subItem.star);
            });
            item.star = (star / item.child_mission.length).toFixed(2);
          });
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

<style lang="stylus" scoped>
.student-name
  font-size:16px;
  color:#333;
  margin-right 20px;
</style>
