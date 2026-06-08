<template>
  <div>
    <div class="pub-filter-box">
      <v-time-bar :timeList="timeLabelList"
                  :handleFunc='timeHandleFunc'
                  @onChange='timeChange'></v-time-bar>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">家长点评</div>
        <div class="count">每月25日10点推出家长点评，1个小时后自动更新点评内容</div>
      </div>
      <el-table :data='listData'
                v-loading='listLoading'
                class='pub-table'>
        <el-table-column label='校区'
                         prop='org_name'></el-table-column>
        <el-table-column label='月份'
                         prop='month'></el-table-column>
        <el-table-column v-for="(item,index) in listHeaderList"
                         :key='index'
                         :label="item">
          <template slot-scope="scope">
            {{scope.row.content[item]}}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text"
                       @click='toDetails(scope.row)'>查看详细</el-button>
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
import { getParentCommentList } from "@/api/statistical";
import timeBar from "@/components/top_box/time_bar";
export default {
  data() {
    return {
      datetime: ["", ""],
      count: 0,
      page: 1,
      size: 10,
      listData: [],
      listLoading: false,
      listHeaderList: [],
      timeLabelList: [
        { label: "近3月", value: "3" },
        { label: "近6月", value: "6" },
        { label: "近12月", value: "12" }
      ],
      timeHandleFunc: {
        enable: true,
        func: function(val) {
          let startDate = new Date(new Date().setHours(0, 0, 0, 0));
          let endDate = new Date().setHours(23, 59, 59, 0);
          startDate = startDate.setMonth(startDate.getMonth() - val);
          return [startDate, endDate];
        }
      }
    };
  },
  components: {
    "v-time-bar": timeBar
  },
  activated() {
    this.$store.dispatch("setTopTitle", { title: "家长点评", des: "家长点评" });
    this.getList();
  },
  methods: {
    getList() {
      let obj = {
        page: this.page,
        count: this.size
      };
      if (this.datetime[0]) {
        obj.start_time = this.datetime[0];
        obj.end_time = this.datetime[1];
      }
      this.listLoading = true;
      getParentCommentList(obj)
        .then(res => {
          console.log(res);
          this.listLoading = false;
          this.listHeaderList = res.data.keyword;
          this.listData = res.data.list;
          this.count = res.data.total / 1;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
          this.$message.error(e);
        });
    },
    timeChange(val) {
      this.datetime = val;
      this.page = 1;
      this.getList();
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    toDetails(item) {
      this.$router.push({
        name: "parentCommentDetails",
        query: { month: item.month, org_id: item.org_id }
      });
    }
  }
};
</script>

