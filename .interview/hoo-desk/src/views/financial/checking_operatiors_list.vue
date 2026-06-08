<template>
  <div>
    <div class='pub-table-wrap'>
      <el-table ref="orderListTable"
                :data="deliver_orders"
                v-loading='tableLoading'
                tooltip-effect="dark"
                class='pub-table'>
        <el-table-column type="index"
                         width="120">
        </el-table-column>

        <el-table-column prop="created_user"
                         label="操作人"
                         width="120">
          <!--<template slot-scope="scope">{{ scope.row.date }}</template>-->
        </el-table-column>
        <el-table-column prop="created_date"
                         label="操作时间"
                         width="120">
          <template slot-scope="scope">
            {{scope.row.created_date | formatToDate("Y-M-D")}}
          </template>
        </el-table-column>
        <el-table-column label="收款金额"
                         prop="deliver_amount"
                         show-overflow-tooltip>
        </el-table-column>

        <el-table-column label="收款方式"
                         show-overflow-tooltip>
          <template slot-scope="scope">
            {{scope.row.payin.payment}}
          </template>
        </el-table-column>

        <el-table-column prop="created_user"
                         label="交款订单"
                         show-overflow-tooltip>
          <template slot-scope="scope">
            <el-button type="text"
                       @click="handleOrderDetail(scope.$index)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <span class="demonstration"></span>
        <el-pagination @current-change="pageChange"
                       :current-page="page"
                       :page-size="page_size"
                       layout="total, prev, pager, next, jumper"
                       :total="total">
        </el-pagination>
      </div>
    </div>
    <!-- 弹出框 -->
    <el-dialog title="订单"
               :visible.sync="payOrderVisiable">
      <div class="pub-table-wrap">
        <div class="table-top-bar">
          <p>操作人员:
            <span>{{selected_deliver.created_user}}</span> 收款金额:
            <span style="color:red;">{{selected_deliver.deliver_amount}}</span>元</p>
        </div>
      </div>
      <el-table :data="order_list"
                border
                class='pub-table'>
        <el-table-column label="订单标题"
                         prop="order_title">
          <template slot-scope="scope">
            <p>{{scope.row.order.order_title}}</p>
          </template>
        </el-table-column>

        <el-table-column label="订单号"
                         prop="order_title">
          <template slot-scope="scope">
            <p>{{scope.row.order.order_sn}}</p>
          </template>
        </el-table-column>

        <el-table-column label="学生"
                         prop="order_title">
          <template slot-scope="scope">
            <p>{{scope.row.order.student.student_name}}</p>
          </template>
        </el-table-column>

        <el-table-column label="订单金额"
                         prop="order_title">
          <template slot-scope="scope">
            <p>{{scope.row.order.receivable_total}}</p>
          </template>
        </el-table-column>

        <el-table-column label="订单日期"
                         prop="order.created_date">
          <template slot-scope="scope">
            {{scope.row.order.created_date | formatToDate("Y-M-D")}}
          </template>
        </el-table-column>

      </el-table>
      <div class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="payOrderVisiable = false">关闭</el-button>
      </div>

    </el-dialog>

  </div>
</template>

<script>
import { getOperatorList } from "@/api/deliver";

export default {
  data() {
    return {
      org_id: 0,
      deliver_order: 0,
      paid_amount: 0,
      refund_amount: 0,
      refund_order: 0,
      receiviable_amount: 0,
      pay_type: 0,
      pay_amount: 0, //交款金额
      order_pay_type: "现金",
      payment_type: "现金", //交款方式
      order_status: 1, //审核状态
      payOrderVisiable: false, //交款确认
      selected_deliver: {},
      payBatchDeleteVisiable: false, //退款确认
      deo_ids: [],
      deliver_orders: [],
      page: 0,
      total: 0,
      page_size: 50,
      search: "",
      datetime: "",
      checkList: "",
      currentTab: "first",
      fee: 0,
      order_list: [],
      options: [
        {
          value: "现金",
          label: "现金"
        },
        {
          value: "转账",
          label: "转账"
        }
      ],
      value: "",
      multipleSelection: [],
      tableLoading: false
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      des: "对账记录",
      title: "对账记录"
    });
  },
  methods: {
    init() {
      this.tableLoading = true;
      getOperatorList(this.page, this.page_size)
        .then(res => {
          this.deliver_orders = res.data.list;
          this.total = parseInt(res.data.count);
          this.tableLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.tableLoading = false;
        });
    },
    pageChange(val) {
      this.page = val;
      this.init();
    },
    handleOrderDetail(val) {
      console.log(val);

      this.order_list = this.deliver_orders[val].orders;
      this.selected_deliver = this.deliver_orders[val];
      this.payOrderVisiable = true;
    }
  },
  mounted() {
    this.init();
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.content
  min-height: 600px;
  .title_wrap
    height: 55px;
    line-height: 55px;
    border-bottom: 1px solid #ebebeb;
    .title
      padding-left: 30px;
    .item
      border-radius: 50% !important;
      padding: 0 3px !important;
      background: #bbbbbb;
      color: #ffffff;
  .creat_wrap
    margin-left: 36px;
    .creat_bt
      width: 120px;
      margin-top: 20px;
    .search_wrap
      height: 82px;
      line-height: 82px;
      .el-input
        width: 239px;
        .el-input__inner
          border-radius: 0 !important;
    .table_wrap
      .date
        height: 40px;
        line-height: 40px;
        font-size: 14px;
        span
          margin-left: 10px;
          color: #BBBBBB;
        .el-checkbox-group
          display: inline-block;
          margin-left: 61px;
      .data:nth-child(0)
        margin-top: 13px;
      .bg_F7
        background: #F7F7F7;
  .line
    height: 1px;
    margin-top: 44px;
    border-bottom: 1px solid #ebebeb;
  .list
    margin-left: 41px;
    margin-top: 23px;
    width: 1110px;
    min-height: 198px;
    border: 1px solid #EEEEEE;
    .list_title
      height: 40px;
      line-height: 40px;
      width: 100%;
      background: #F9F9F9;
      border-bottom: 1px solid #EEEEEE;
      .title_name
        margin-left: 20px;
      .upload
        float: right;
        margin-right: 17px;
    .list_handle
      height: 54px;
      line-height: 54px;
      .tips
        display: inline;
        margin-left: 20px;
        font-size: 14px;
        font-weight: bold;
        height: 20px;
        border-left: 4px solid #101010;
    .el-table
      .coursestatus
        display: inline-block;
        height: 20px;
        line-height: 20px;
        padding: 0 8px;
        border-radius: 4px;
        font-weight: bold;
        color: #FFFFFF;
      .bg_E5
        background: #E51C23;
      .bg_FF
        background: #FF9800;
      .bg_55
        background: #555555;
      .handle_eidt
        width: 20px;
        height: 20px;
        vertical-align: middle;
    .pagination
      margin-top: 50px;
      padding-bottom: 32px;
  .real_time_data
    ul
      display: flex;
      li
        text-align: center;
        height: 158px;
        border-right: 1px solid #eeeeee;
        flex: 2;
        .data_name
          margin-top: 29px;
          font-size: 13px;
        .data_num
          margin-top: 6px;
          font-weight: bold;
          font-size: 30px;
          span
            font-weight: bold;
            font-size: 30px;
        .data_percent
          margin-top: 7px;
      &>li:last-child
        border-right: none;
        flex: 3;
</style>
