<template>
  <div>
    <div class="data-box">
      <div class="tips-bar">交款汇总</div>
      <el-row type="flex" v-if="result">
        <el-col class="data-item">
          <p class="data_name">交款订单</p>
          <p class="data_num">
            <span style="color:#E51C23;">{{result.order_total['总计'].count}}&ensp;份</span>
          </p>
          <p class="data_name">总金额</p>
          <p class="data_num">
            <span>{{result.order_total['总计'].amount}}&ensp;元</span>
          </p>
        </el-col>
        <el-col class="data-item received-wrap" v-if="type != 1">
          <div
            v-for="(item,index) in result.show_already_paid"
            :key="index"
            class="received-item"
            v-if="item.payment !=='总计'"
          >
            <p class="data_name">已收{{item.payment}}</p>
            <p class="data_num">
              <span>{{item.num}}&ensp;元</span>
            </p>
          </div>
        </el-col>
        <el-col class="data-item" v-if="type == 1">
          <p class="data_name">已收金额</p>
          <p class="data_num">
            <span style="color:#E51C23;">{{result.already_paid["总计"]}}&ensp;元</span>
          </p>
        </el-col>
        <el-col class="data-item">
          <p class="data_name">应收金额</p>
          <p class="data_num">
            <span style="color:#E51C23;">{{receiviable_amount}}&ensp;元</span>
          </p>
        </el-col>
        <el-col class="data-item">
          <p class="data_name">
            <el-select v-model="payment_type" placeholder="请选择交款方式" @change="chooseType">
              <el-option
                size="mini"
                v-for="(item,index) in result.show_already_paid"
                v-if="item.payment !== '总计'"
                :key="index"
                :label="item.payment"
                :value="item.payment"
              ></el-option>
            </el-select>
          </p>
          <el-input v-model="pay_amount" style="margin:10px 0;width:200px;" placeholder="请输入交款金额"></el-input>
          <p class="data_num">
            <el-button @click="showPaymentDialog()">确认交款</el-button>
          </p>
        </el-col>
      </el-row>
    </div>
    <v-table-wrap 
      :page='page'
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      noFilter
      :total="orderTotal"
    >
      <template slot="table_title">缴费详情</template>
      <el-button slot="table_btns" @click="toExport">导出订单</el-button>
      <el-button slot="table_btns" @click="backOrder" v-if="result.status == 0">一键退回</el-button>
      <template slot="table_count">
        <span
          v-for="(item,index) in result.show_order_total"
          :key="index"
          style="margin-left: 10px"
          v-if=" type !=1 || (type == 1 && index != 0 && index!=1)"
        >
          <i>{{item.payment}}</i>:
          <i>{{item.amount}}({{item.count}}笔)</i>
        </span>
      </template>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="orderList"
        v-loading="tableLoading"
        tooltip-effect="dark"
        class="pub-table"
      >
        <el-table-column prop="order_sn" label="订单编号"></el-table-column>
        <el-table-column prop="amount" label="收款金额" show-overflow-tooltip></el-table-column>
        <el-table-column prop="payment" label="收款方式" show-overflow-tooltip></el-table-column>
        <el-table-column v-if="type!=1" label="收款人" show-overflow-tooltip prop="created_user"></el-table-column>
        <el-table-column v-if="type!=1" label="审核人">
          <template slot-scope="scope">{{updated_user ? updated_user : "暂无"}}</template>
        </el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column label="报名课程(课时数、直减、折扣)" width="400">
          <template slot-scope="scope">
            <p v-for="(item,index) in scope.row.order.orderCourses" :key="index">{{calText(item)}}</p>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="所属分校"></el-table-column>
        <el-table-column prop="created_date" label="收款时间" width="180">
          <template slot-scope="scope">{{scope.row.created_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <!-- 弹出框 -->
    <el-dialog width="400px" title="确认交款" :visible.sync="payOrderVisiable">
      <div class="flex-block">
        <span class="title">交款总金额</span>
        <span style="color:red;">{{receiviable_amount}}</span>
      </div>

      <div class="flex-block">
        <span class="title">交款方式</span>
        <span style="color:red;">{{payment_type}}</span>
      </div>
      <div class="flex-block">
        <p style="font-size:12px">温馨提示:财务人员审核，并确认。</p>
      </div>

      <div slot="footer" class="dialog-footer" style="text-align:right">
        <el-button type="primary" @click="handleDeliverPay()">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { deliverPay } from "@/api/deliver";
import { paymentDetail, postPay, oneBack, exportList } from "@/api/order";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      org_id: 0,
      receiviable_amount: 0,
      pay_amount: "", //交款金额
      order_pay_type: "",
      payment_type: "", //交款方式
      payOrderVisiable: false, //交款确认
      page: 1,
      orderTotal: 0,
      size: 10,
      orderList: [],
      result: "",
      tableLoading: false,
      type: "", //1 为小程序
      updated_user: "", //审核人
      payMethodList: []
    };
  },
  created() {
    if (this.$route.query.type / 1 !== 0) {
      this.type = this.$route.query.type;
      this.payMethodList = ["在线支付"];
      this.order_pay_type = "在线支付";
      this.payment_type = "在线支付";
    }
    this.init();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    toExport() {
      exportList({ der_id: this.$route.query.der_id, type: this.type })
        .then(res => {
          this.$downLoad(res.data);
          this.$message.success("导出成功");
        })
        .catch(e => {
          this.$message.error("导出失败");
          console.log("e", e);
        });
    },
    init() {
      let obj = {
        der_id: this.$route.query.der_id,
        page: this.page,
        size: this.size,
        type: this.type
      };
      this.tableLoading = true;
      paymentDetail(obj)
        .then(res => {
          let result = res.data;
          this.result = result;
          this.orderTotal = parseInt(result.order_payin_count);
          this.orderList = result.order_payin;
          let calcType = this.payment_type !== "" ? this.payment_type : "总计";
          this.receiviable_amount = (
            this.result.order_total[calcType].amount - this.result.already_paid[calcType]
          ).toFixed(2);

          // this.type == 1
          //   ? (this.receiviable_amount =
          //       this.result.order_total[3].amount -
          //       this.result.already_paid[2].amount)
          //   : (this.receiviable_amount =
          //       this.result.order_total[0].amount -
          //       this.result.already_paid[0].amount);
          console.log("this.orderList", this.orderList);
          result.show_already_paid = Object.keys(result.already_paid).map((val, index) => {
            return { payment: val, num: result.already_paid[val] };
          });
          result.show_order_total = Object.keys(result.order_total).map((val, index) => {
            return { payment: val, ...result.order_total[val] };
          });
          this.tableLoading = false;
          this.updated_user = res.data.updated_user;
        })
        .catch(error => {
          this.tableLoading = false;
          console.log(error);
        });
    },
    backOrder() {
      this.$confirm("此操作将退回该订单, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            der_id: this.$route.query.der_id
          };
          oneBack(obj)
            .then(res => {
              this.$message.success("退回成功");
              this.$router.back();
            })
            .catch(error => {
              this.$message.error("退回失败");
            });
        })
        .catch(e => {});
    },
    handlePaymentChange(val) {
      this.order_pay_type = val;
      this.init();
    },
    //交款确认
    showPaymentDialog() {
      if (this.receiviable_amount == 0) {
        this.$message.error("金额不能为零");
        return false;
      }
      if (this.pay_amount / 1 !== this.receiviable_amount / 1) {
        this.$message.error("金额不对，请重输");
        return false;
      }

      this.payOrderVisiable = true;
    },
    //交款
    handleDeliverPay() {
      let obj = {
        org_id: this.$route.query.org_id,
        der_id: this.$route.query.der_id,
        amount: this.pay_amount,
        payment: this.payment_type
      };
      postPay(obj)
        .then(res => {
          this.$message.success("交款成功");
          this.payOrderVisiable = false;
          this.pay_amount = "";
          this.init();
        })
        .catch(error => {
          this.$message.error("交款失败");
        });
    },
    chooseType(data) {
      this.receiviable_amount =
        this.result.order_total[data].amount - this.result.already_paid[data];
    },
    calText(item) {
      // 课程名称(课次*单次课时、折扣率((直减+折扣金额)/单价/课时数))
      let { course_name, hours, times,reduce, discount } = item;
      return `${item.course_name}(${(hours * times).toFixed(
        2
      )}课时、${reduce}元、${discount}%)`;
    }
  },
  components: {
    "v-table-wrap": tableTemplate
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.data-box
  padding: 20px 20px 0;
  .data-item
    border: 1px solid #eee;
    padding-bottom: 20px;
    text-align: center;
  .data_name
    margin-top: 15px;
    font-size: 13px;
  .data_num
    margin-top: 6px;
    font-weight: bold;
    font-size: 30px;
    button
      font-size: 14px;
    span
      font-weight: bold;
      font-size: 20px;
  .received-wrap
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
  .received-item
    flex: 0 0 50%;
</style>
