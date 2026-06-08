<template>
  <div class="pub-table-wrap">
    <el-table :data="tableList" v-loading="tableLoading" class="pub-table">
      <el-table-column label="姓名" prop="member_name"></el-table-column>
      <el-table-column label="电话" prop="member_phone"></el-table-column>
      <el-table-column label="红包总金额" prop="total"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="getInfo(scope.row)">红包明细</el-button>
        </template>
      </el-table-column>
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
    <el-dialog width="500px" v-loading="infoLoading" :visible.sync="dialogShow" title="红包明细">
      <el-table max-height="500" style="margin:0" :data="infoList" class="pub-table">
        <el-table-column label="红包金额" prop="amount"></el-table-column>
        <el-table-column label="领取时间">
          <template slot-scope="scope">{{scope.row.create_time | formatToDate}}</template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>


<script>
import { getRedPackUser, getRedPackUserList } from "@/api/group_course";
export default {
  data() {
    return {
      dialogShow: false,
      tableList: [],
      tableLoading: false,
      page: 1,
      size: 10,
      count: 0,
      infoLoading: false,
      infoList: []
    };
  },
  created() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "获得红包用户列表",
      desc: "获得红包用户列表"
    });
  },
  methods: {
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    getInfo(item) {
      this.dialogShow = true;
      this.getInfoList(item);
    },
    getInfoList(item) {
      this.infoLoading = true;
      getRedPackUserList({
        size: 10000,
        member_id: item.member_id,
        course_id: this.$route.query.course_id
      })
        .then(res => {
          console.log("res", res);
          this.infoList = res.data.list;
          this.infoLoading = false;
        })
        .catch(e => {
          console.log("error", e);
          this.infoLoading = false;
          this.$message.error(e);
        });
    },
    getList() {
      this.tableLoading = true;
      getRedPackUser({
        page: this.page,
        size: this.size,
        course_id: this.$route.query.course_id
      })
        .then(res => {
          console.log("res", res);
          this.tableList = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log("error", e);
          this.tableLoading = false;
          this.$message.error(e);
        });
    }
  }
};
</script>
