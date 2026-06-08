<template>
  <div class="balance-setting">
    <!-- <div class="pub-filter-box">
      <div class="btn-bar">
        <el-radio-group v-model="navSelect"
                        @change="navChange">
          <el-radio v-for="(item,index) in navList"
                    :key="index"
                    :label="item.pathName">{{item.text}}</el-radio>
        </el-radio-group>
      </div>
    </div> -->
    <div class="pub-table-wrap">
      <el-table v-loading='tableLoading'
                :data="refundList"
                class='pub-table'>
        <el-table-column prop="student_name"
                         label='学生姓名'></el-table-column>
        <el-table-column label='来源'>
          <template slot-scope="scope">钱包余额提现</template>
        </el-table-column>
        <el-table-column label='类型'>
          <template slot-scope="scope">退款</template>
        </el-table-column>
        <el-table-column prop="pay_money"
                         label='金额'></el-table-column>
        <el-table-column prop="card_holder"
                         label='收款人'></el-table-column>
        <el-table-column prop="bank_name"
                         label='银行'></el-table-column>
        <el-table-column prop="card_number"
                         label='账号'></el-table-column>
        <el-table-column label="申请时间">
          <template slot-scope="scope">{{scope.row.created_date | formatToDate}}</template>
        </el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       v-if="scope.row.status == 0"
                       @click='refundHandler(scope.row,true)'>通过</el-button>
            <el-button type='text'
                       v-if="scope.row.status == 0"
                       @click='refundHandler(scope.row,false)'>拒绝</el-button>
            <p v-if="scope.row.status == 2">已通过</p>
            <p v-if="scope.row.status == 3">已拒绝</p>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination @current-change="pageChange"
                       :current-page.sync="page"
                       :page-size="size"
                       layout=" total, prev, pager, next"
                       :total="count">
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import { getRefundList, handleRefund } from "@/api/balance";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      navSelect: "unrefund_list",
      refundList: [],
      navList: [],
      tableLoading: false
    };
  },
  created() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "结算管理",
      des: "结算管理"
    });
    this.navList = this.$store.state.financial.nvaList;
  },
  methods: {
    navChange(val) {
      this.$router.push({ name: val });
    },
    // 获取申请提现列表
    getList() {
      this.tableLoading = true;
      getRefundList({ page: this.page, size: this.size,type:1 })
        .then(res => {
          console.log("获取提现申请列表返回", res);
          this.refundList = res.data.list;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    //提现操作
    refundHandler(row, status) {
      let str = status == true ? "确定同意提现申请?" : "确定拒绝提现申请?";
      this.$confirm(str, "提示", { type: "warning" })
        .then(() => {
          let params = {
            id: row.id,
            type: status == true ? 1 : 0
          };
          return handleRefund(params);
        })
        .then(res => {
          console.log("同意或拒绝返回", res);
          this.$message.success(res.msgs);
          this.getList();
        })
        .catch(e => {
          // console.log(e);
          if (e != "cancel") {
            console.log(e);
            this.$message.error(res.msgs);
          }
        });
    },
    //翻页
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  }
};
</script>

<style scoped lang="stylus">
.pub-filter-box
  .btn-bar
    .el-radio
      border: 1px solid #ebebeb;
      padding: 10px 20px;
      border-radius: 5px;
</style>
