<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'pageCount')"
    >
      <el-button slot="buttons" type="primary" @click="creatAccount">银行账户管理</el-button>
      <div class="btn-bar" slot="searchItems">每周结算2次，周二、周五下午5点，云翰管家将自动打款到指定收款账户。微信支付手续费1%。</div>
      <template slot="table_title">结算列表</template>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{count}}</i>个记录
      </div>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        class="pub-table"
        v-loading="tableLoading"
      >
        <el-table-column type="index" label="序号"></el-table-column>
        <el-table-column prop="created_date" label="结算日期"></el-table-column>
        <el-table-column prop="card_holder" label="收款人"></el-table-column>
        <el-table-column prop="card_number" label="收款账号"></el-table-column>
        <el-table-column prop="pay_money" label="金额"></el-table-column>
        <el-table-column prop="type" label="结算状态">
          <template slot-scope="scope">
            <span v-if="scope.row.status == 0">财务待确认</span>
            <span v-if="scope.row.status == 1">财务已确认</span>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import tableTemplate from "@/components/listViewTemplate";
import { getBalanceRecordList } from "@/api/balance";
export default {
  data() {
    return {
      datetime: "",
      checkList: "",
      size: 10, //分页每页显示10条
      count: 0,
      page: 1,
      tableData: [],
      multipleSelection: [],
      order_list: [],
      tableLoading: false
    };
  },
  activated() {
    this.getList();
  },
  methods: {
    getList() {
      let obj = {
        page: this.page,
        count: this.size
      };
      this.tableLoading = true;
      getBalanceRecordList(obj)
        .then(res => {
          let listData = res.data.list;
          if (listData.length != 0) {
            this.tableData = listData;
            this.count = Number(res.data.count);
          }
          this.tableLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.tableLoading = false;
        });
    },
    // 新增银行卡账号
    creatAccount() {
      this.$router.push({
        path: "./create_account",
        query: {}
      });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    }
  },
  components: {
    "v-table-wrap": tableTemplate
  }
};
</script>

