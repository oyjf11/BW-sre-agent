<template>
  <div v-loading.lock="dataLoading">
    <div class="pub-filter-box">
      <v-time-bar
        :time="datetime"
        :timeList="timeLabelList"
        :handleFunc="timeHandleFunc"
        :timePickerOption="timePickerOption"
        @onChange="timeChange"
      ></v-time-bar>
      <v-search-bar placeholder="请输入分校名" @onSearch="toSearch"></v-search-bar>
    </div>
    <div class="pub-table-wrap">
      <div class="data-box">
        <div class="tips-bar">实时数据</div>
        <el-row type="flex">
          <el-col class="data-item">
            <p class="data_name">订单总数</p>
            <p class="data_num">
              <span>{{all_order_count}}&ensp;份</span>
            </p>
          </el-col>
          <el-col class="data-item">
            <p class="data_name">已收总额</p>
            <p class="data_num">
              <span style="color:#E51C23;">{{all_received}}&ensp;元</span>
            </p>
            <p class="data_name">应收总额</p>
            <p class="data_num">
              <span>{{all_receivable}}&ensp;元</span>
            </p>
          </el-col>
          <el-col class="data-item">
            <p class="data_name">已提交财务</p>
            <p class="data_num">
              <span style="color:#E51C23;">{{all_unconfirmed}}&ensp;元</span>
            </p>
            <p class="data_name">未提交财务</p>
            <p class="data_num">
              <span>{{all_unpaid_amount}}&ensp;元</span>
            </p>
          </el-col>
          <el-col class="data-item">
            <p class="data_name">钱包余额</p>
            <p class="data_num">
              <el-button type="text" @click="toBalanceTotalList(0)">{{total_balance}}&ensp;元</el-button>
            </p>
            <p class="data_name">未退款总金额</p>
            <p class="data_num">
              <el-button type="text" @click="toBalanceTotalList(1)">{{total_refund_balance}}&ensp;元</el-button>
            </p>
          </el-col>
          <el-col class="data-item">
            <p class="data_name">已确认提交</p>
            <p class="data_num">
              <span>{{all_paid_amount}}&ensp;元</span>
            </p>
          </el-col>
        </el-row>
      </div>

      <div class="table-top-bar" style="margin-top:20px;">
        <div class="title">详细数据</div>
        <el-button class="btn" @click="exportExcel()">数据导出</el-button>
      </div>
      <el-table :data="orderData" border height="500px" class="pub-table out-table">
        <el-table-column label="分校" :resizable="false" prop="org_name"></el-table-column>
        <el-table-column label="汇总">
          <el-table-column label="订单" :resizable="false" prop="order_count"></el-table-column>
          <el-table-column label="收费" :resizable="false" prop="pay_count"></el-table-column>
          <el-table-column label="打印" :resizable="false" prop="log_count"></el-table-column>
          <el-table-column label="应收" :resizable="false" prop="total_receivable" sortable></el-table-column>
          <el-table-column label="已收" :resizable="false" prop="total_received" sortable></el-table-column>
          <el-table-column label="差额" :resizable="false" prop="total_diff_amount" sortable></el-table-column>
          <el-table-column label="已交" :resizable="false" prop="total_paid_amount" sortable></el-table-column>
          <el-table-column label="最后交款日期" prop="deliver_date" sortable min-width="115">
            <template slot-scope="scope">
              <template
                v-if="scope.row.deliver_date"
              >{{scope.row.deliver_date | formatToDate("Y-M-D")}}</template>
              <template v-else>未设置交款时间</template>
            </template>
          </el-table-column>
          <el-table-column label="未交" :resizable="false" prop="total_unpaid_amount" sortable></el-table-column>
          <el-table-column
            label="已提交未确认"
            min-width="115"
            :resizable="false"
            prop="total_unconfirmed"
            sortable
          ></el-table-column>
        </el-table-column>
        <el-table-column label="未交明细">
          <el-table-column v-for="(item,index) in payMethodList" :key="index" :label="item">
            <template
              slot-scope="scope"
            >{{scope.row.total_unpaid_detail[item] ? (scope.row.total_unpaid_detail[item]/1).toFixed(2) :0}}</template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="未确认明细">
          <el-table-column v-for="(item,index) in payMethodList" :key="index" :label="item">
            <template
              slot-scope="scope"
            >{{scope.row.total_unconfirmed_detail[item] ? (scope.row.total_unconfirmed_detail[item]/1).toFixed(2) :0}}</template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" width="200">
          <template slot-scope="scope">
            <div>
              <el-button type="text" @click="clickFinancialVerify(scope.row.org_id)" small>交款审核</el-button>
              <el-button type="text" @click="clickOrderList(scope.row.org_id)">分校订单</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import FileSaver from "file-saver";
let XLSX;
import(/* webpackChunkName: "group-xlsx" */ /* webpackMode: "lazy" */ "xlsx").then(
  res => {
    XLSX = res;
  }
);
import { getOrderData } from "@/api/financial";
import searchBar from "@/components/top_box/search_bar";
import timeBar from "@/components/top_box/time_bar";
export default {
  data() {
    let start = new Date().setHours(0, 0, 0, 0) - 3600 * 1000 * 24 * 30;
    let end = new Date().setHours(23, 59, 59, 0);
    return {
      search: {
        org_name: ""
      },
      datetime: [start / 1000, end / 1000],
      checkList: "",
      page: 1,
      count: 0,
      total: 0,
      handleDate: 30,
      all_order_count: 0,
      all_paid_amount: 0,
      all_receivable: 0,
      all_received: 0,
      all_unconfirmed: 0,
      all_unpaid_amount: 0,
      total_balance: 0,
      total_refund_balance: 0,
      orderData: [],
      multipleSelection: [],
      timePickerOption: {
        options: {
          disabledDate(time) {
            return time.getTime() > Date.now();
          }
        }
      },
      dataLoading: false,
      payMethodList: [],
      timeLabelList: [
        { label: "7天", value: "7" },
        { label: "14天", value: "14" },
        { label: "30天", value: "30" }
      ],
      timeHandleFunc: {
        enable: true,
        func: function(val) {
          let startDate = new Date().setHours(0, 0, 0, 0);
          let endDate = new Date().setHours(23, 59, 59, 0);
          if (val === "all") {
            startDate = startDate - 3600 * 1000 * 24 * 365 * 10;
          } else {
            startDate = startDate - (val - 1) * 24 * 60 * 60 * 1000;
          }
          return [startDate, endDate];
        }
      }
    };
  },
  components: {
    "v-search-bar": searchBar,
    "v-time-bar": timeBar
  },
  methods: {
    //跳转到钱包记录
    toBalanceTotalList(val) {
      this.$router.push({ name: val === 0 ? "balance_detail" : "unrefund_list" });
    },
    init() {
      this.dataLoading = true;
      getOrderData(
        this.page,
        this.count,
        this.search,
        this.datetime[0],
        this.datetime[1]
      )
        .then(res => {
          let result = res.data;
          this.all_order_count = this.formatMoney(result.all_order_count, 2);
          this.all_order_count = this.all_order_count.split(".")[0];
          this.all_paid_amount = this.formatMoney(result.all_paid_amount, 2);
          this.all_receivable = this.formatMoney(result.all_receivable, 2);
          this.all_received = this.formatMoney(result.all_received, 2);
          this.all_unconfirmed = this.formatMoney(result.all_unconfirmed, 2);
          this.all_unpaid_amount = this.formatMoney(
            result.all_unpaid_amount,
            2
          );
          this.total_refund_balance = this.formatMoney(
            result.total_refund_balance,
            2
          );
          this.total_balance = this.formatMoney(result.total_balance, 2);
          this.total = parseInt(result.count);
          this.orderData = result.list;
          this.payMethodList = result.payment_title;
          this.dataLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.dataLoading = false;
        });
    },
    toSearch(val) {
      this.search.org_name = val;
      this.init();
    },
    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    timeChange(val) {
      this.datetime = val;
      this.init();
    },
    clickFinancialVerify(org_id) {
      this.$router.push({
        name: "payment_records",
        query: {
          org_id: org_id
        }
      });
    },
    clickOrderList(org_id) {
      this.$router.push({
        name: "toll_data",
        query: {
          org_id: org_id
        }
      });
    },
    arraySpanMethod({ row, column, rowIndex, columnIndex }) {
      for (let i = 0; i < 2; i++) {
        let x = 3 * i + 2;
        if (columnIndex == x) {
          console.log("x", x);
          return [[x, x + 1, x + 2]];
        }
      }
    },
    //金额换算
    formatMoney(value, type = 1) {
      if (type == 1) {
        return parseInt(value / 1000);
      } else {
        if (!value) return "0.00";
        //获取整数部分
        // var intPart = Number(value) < 1 ? 0 : Number(value).toFixed(0);
        var intPart = Math.floor(value);
        //将整数部分逢三一断
        var intPartFormat = intPart
          .toString()
          .replace(/(\d)(?=(?:\d{3})+$)/g, "$1,");
        //预定义小数部分
        var floatPart = ".00";
        var value2Array = value.toString().split(".");

        //=2表示数据有小数位
        if (value2Array.length == 2) {
          floatPart = value2Array[1].toString(); //拿到小数部分
          if (floatPart.length == 1) {
            //补0,实际上用不着
            return intPartFormat + "." + floatPart + "0";
          } else {
            return intPartFormat + "." + floatPart;
          }
        } else {
          return intPartFormat + floatPart;
        }
      }
    },
    exportExcel() {
      /* generate workbook object from table */
      var wb = XLSX.utils.table_to_book(document.querySelector(".out-table"));
      /* get binary string as output */
      var wbout = XLSX.write(wb, {
        bookType: "xlsx",
        bookSST: true,
        type: "array"
      });
      try {
        FileSaver.saveAs(
          new Blob([wbout], { type: "application/octet-stream" }),
          "orderData.xlsx"
        );
      } catch (e) {
        if (typeof console !== "undefined") console.log(e, wbout);
      }
      return wbout;
    },
    toaudit() {
      this.$router.push({
        path: "/financial/audit"
      });
    }
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "缴费对账",
      des: "实时查看订单数、已收金额、应收金额等重要财务数据。"
    });
    this.init();
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.data-box
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
      font-size: 20px;
    span
      font-weight: bold;
      font-size: 20px;
</style>
