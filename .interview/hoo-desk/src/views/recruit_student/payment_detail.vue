<template>
  <div>
    <v-table-wrap
      showSearch
      :page="page"
      :total="orderTotal"
      :pageSizes="[30,50, 100, 200]"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      placeholder="请输入搜索内容"
      @onSearch="filterChange($event,'search')"
    >
      <v-radio-bar
        slot="searchItems"
        label="收款方式"
        :radioList="payMethodList"
        @onChange="filterChange($event,'payment')"
      ></v-radio-bar>
      <div slot="table_btns">
          <el-button @click="toExport">数据导出</el-button>
          <el-button @click="exportTable">预收表导出</el-button>
        </div>
      <div slot="table_count">
        <span v-for="(item,index) in show_order_total" :key="index">
          <i>{{item.payment}}</i>:
          <i>{{item.amount.toFixed(2)}}({{item.count}}笔)</i>
        </span>
      </div>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="orderList"
        v-loading="tableLoading"
        tooltip-effect="dark"
        class="pub-table"
      >
        <el-table-column prop="order_sn" label="订单编号"></el-table-column>
        <el-table-column prop="amount" label="收款金额"></el-table-column>
        <el-table-column prop="payment" label="收款方式"></el-table-column>
        <el-table-column label="收款人" prop="created_user"></el-table-column>
        <el-table-column label="审核人">
          <template slot-scope="scope">{{created_user}}</template>
        </el-table-column>
        <el-table-column label="对账人">
          <template slot-scope="scope">{{updated_user}}</template>
        </el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="order_title" label="报名课程"></el-table-column>
        <el-table-column prop="org_name" label="所属分校"></el-table-column>
        <el-table-column prop="created_date" label="收款时间">
          <template slot-scope="scope">{{scope.row.created_date | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作" show-overflow-tooltip>
          <template slot-scope="scope">
            <div>
              <el-button @click="goApply(scope.row)" type="text" size="small">查看订单</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import {
  deliverList,
  delOrder,
  easyPost,
  oneKey,
  paymentRecords,
  paymentDetail,
  exportList
} from "@/api/order";
import { apply, reapply, cancel, exportTable } from "@/api/financial";
import tableTemplate from "@/components/listViewTemplate";
import radioBar from "@/components/top_box/radio_bar";
import { getPayMethod } from "@/api/operations_center";
import searchBar from "@/components/top_box/search_bar";
export default {
  data() {
    return {
      payment: "",
      org_id: 0,
      search: "",
      checkList: "",
      orderTotal: 0,
      page: 1, //分页每页显示10条
      size: 30,
      orderList: [],
      multipleSelection: [],
      end_date: "",
      isApply: false,
      remark: "",
      selectRows: {},
      result: {},
      der_id: "",
      tableLoading: false,
      created_user: "",
      updated_user: "",
      payMethodList: [],
      show_order_total:[]
    };
  },
  created() {
    this.end_date = ~~(new Date().getTime() / 1000);
    this.der_id = this.$route.query.der_id;
    this.getPayMethod();
    this.init();
  },
  components: {
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate,
    "v-radio-bar": radioBar
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    getPayMethod() {
      getPayMethod({ attr_name: "payment" })
        .then(res => {
          this.payMethodList = []
          for (let i in res.data) {
            let _obj = {
              label: res.data[i], value: res.data[i]
            }
            this.payMethodList.push(_obj)
          }
        })
        .catch(e => {
          console.log(e);
        });
    },
    //预收表导出
    exportTable() {
      exportTable({ der_id: this.der_id })
        .then(res => {
          console.log("res", res);
          window.location.href = res.data;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("导出失败");
        });
    },
    // 注册方法
    goCreat() {
      this.$router.push({
        path: "/recruit_student/creat_student"
      });
    },
    //数据导出
    toExport() {
      exportList({ der_id: this.der_id })
        .then(res => {
          // let a = document.createElement("a");
          // a.href = res.data;
          // a.style.display = "none";
          // document.body.appendChild(a);
          // a.click();
          // a.remove();
          this.$downLoad(res.data)
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    init() {
      let obj = {
        der_id: this.der_id,
        page: this.page,
        size: this.size,
        payment: this.payment,
        search: this.search
      };
      this.tableLoading = true;
      paymentDetail(obj)
        .then(res => {
          let result = res.data;
          this.result = result;
          this.orderTotal = parseInt(result.order_payin_count);
          this.orderList = result.order_payin;
          this.created_user = res.data.created_user ? res.data.created_user : "暂无";
          this.updated_user = res.data.updated_user ? res.data.updated_user : "暂无";
          this.show_order_total = Object.keys(result.order_total).map((val, index) => {
            return { payment: val, ...result.order_total[val] };
          });
          this.tableLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.tableLoading = false;
        });
    },
    toCreatStudent() {
      this.$router.push({
        path: "/recruit_student/creat_student"
      });
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
    //      提交订单
    postDeliver() {
      var time = new Date();
      //        this.allSelect();
      //        console.log(time.getTime());
      let obj = {
        closing_date: this.end_date
      };
      this.$confirm("此操作将所有订单提交, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          oneKey(obj)
            .then(res => {
              console.log("res", res);
              this.$message.success("提交成功");
              this.init();
            })
            .catch(error => {
              this.$message.error(error);
            });
        })
        .catch(() => {});
    },
    goApply(rows) {
      this.$router.push({
        name: "order_detail_new",
        query: {
          order_id: rows.order_id
        }
      });
    },
    remove() {
      this.selectRows = {};
      this.isApply = false;
      this.remark = "";
      //        this.handleType = 0;
    },
    save() {
      let obj = {
        order_id: this.selectRows.payin_id,
        remark: this.remark
      };
      apply(obj)
        .then(res => {
          this.init();
          this.remove();
          this.remark = "";
        })
        .catch(error => {
          this.remove();
        });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>
