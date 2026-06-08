<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="orderTotal"
      showSearch
      placeholder="请输入搜索内容"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      @onSearch="filterChange($event,'search')"
    >
      <v-radio-bar
        slot="searchItems"
        label="收款方式"
        @onChange="filterChange($event,'payment')"
        :radioList="payMethodList"
      ></v-radio-bar>
      <el-button slot="table_btns" type="primary" @click="postDeliver">提交</el-button>
      <el-button slot="table_btns" @click.stop.prevent="download">数据导出</el-button>
      <div slot="table_count">
        <span v-for="(item,index) in result.show_info" :key="index" style="margin-right:20px">
          <i>{{item.payment}}</i>:
          <i>{{item.amount.toFixed(2)}}({{item.count}}笔)</i>
        </span>
      </div>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="orderList"
        tooltip-effect="dark"
        v-loading="tableLoading"
        class="pub-table"
      >
        <el-table-column prop="order_sn" label="订单编号"></el-table-column>
        <el-table-column prop="amount" label="收款金额"></el-table-column>
        <el-table-column prop="payment" label="收款方式"></el-table-column>
        <el-table-column label="收款人" prop="created_user"></el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column label="报名课程(课时数、直减、折扣)" width="400">
          <template slot-scope="scope">
            <p v-for="(item,index) in scope.row.order.orderCourses" :key="index">{{calText(item)}}</p>
          </template>
        </el-table-column>
        <el-table-column label="时间" prop="created_date" width='160' >
          <template slot-scope="scope">{{scope.row.created_date | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <div v-if="scope.row.is_del == 0">
              <el-button @click="goApply(scope.row)" type="text" size="small">申诉</el-button>
            </div>
            <div v-if="scope.row.is_del == 1">订单已注销</div>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog title="原因" :visible.sync="isApply" width="30%" center>
      <textarea v-model="remark" style="width:100%;height:80%" rows="8" cols="10"></textarea>
      <span slot="footer" class="dialog-footer">
        <el-button @click="remove()">取 消</el-button>
        <el-button type="primary" @click="save()">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  deliverList,
  delOrder,
  easyPost,
  oneKey,
  goDownload
} from "@/api/order";
import { apply, reapply, cancel } from "@/api/financial";
import { getPayMethod } from "@/api/operations_center";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      payment: "",
      org_id: 0,
      search: "",
      checkList: "",
      orderTotal: 0,
      page: 1, //分页每页显示10条
      size: 50,
      orderList: [],
      multipleSelection: [],
      id_list: [],
      start_date: new Date().getTime() - 60 * 60 * 24 * 365 * 1000,
      end_date: "",
      isApply: false,
      remark: "",
      selectRows: {},
      result: {},
      datetime: [
        new Date().getTime() - 60 * 60 * 24 * 365 * 1000,
        new Date().getTime()
      ],
      tableLoading: false,
      payMethodList: []
    };
  },
  created() {
    this.end_date = ~~(new Date().getTime() / 1000);
    this.$store.dispatch("setTopTitle", {
      des: "缴费订单",
      title: "一键审核"
    });
    this.init();
    this.getPayMethod();
  },
  components: {
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate
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
          // this.payMethodList = res.data;
          this.payMethodList = res.data.map(i => {
            return { label: i, value: i };
          });
        })
        .catch(e => {
          console.log(e);
        });
    },
    // 课程编辑
    handleClick(data) {
      this.$router.push({
        name: "order_detail_new",
        query: {
          order_id: data.order_id
        }
      });
    },
    init(string) {
      let org_id = this.$route.query.org_id;
      this.org_id = org_id;
      let obj = {
        org_id: org_id,
        page: this.page,
        size: this.size,
        search: this.search,
        closing_date: this.end_date,
        payment: this.payment
      };
      this.tableLoading = true;
      easyPost(obj)
        .then(res => {
          let result = res.data;
          this.result = result;
          this.orderTotal = parseInt(result.count);
          this.orderList = result.list;
          for (let i = 0; i < this.orderList.length; i++) {
            this.$set(this.orderList[i], "isChecked", false);
          }
          this.result.show_info = Object.keys(this.result.info).map(
            (val, index) => {
              return { payment: val, ...result.info[val] };
            }
          );
          this.tableLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.tableLoading = false;
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

    //      提交订单
    postDeliver() {
      var time = new Date();
      let obj = {
        closing_date: this.end_date
      };
      let str = "";
      for (let i = 0; i < this.result.show_info.length; i++) {
        str += `${this.result.show_info[i].payment}:${
          this.result.show_info[i].amount
        }(${this.result.show_info[i].count})笔、`;
      }
      str = str.substring(0, str.length - 1);
      this.$confirm(str, "是否继续?", "提示", {
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
              this.$router.push({
                name: "toll_data",
                query: {
                  isShowCount: 1
                }
              });
            })
            .catch(error => {
              this.$message.error(error);
            });
        })
        .catch(() => {});
    },
    goApply(rows) {
      this.selectRows = rows;
      this.isApply = true;
    },
    remove() {
      this.selectRows = {};
      this.isApply = false;
      this.remark = "";
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
    },
    download() {
      let obj = {
        closing_date: this.end_date
      };
      goDownload(obj)
        .then(res => {
          console.log("下载", res);
          window.location.href = res.data;
        })
        .catch(error => {
          this.$message.error("导出失败");
        });
    },
    calText(item) {
      // 课程名称(课次*单次课时、折扣率((直减+折扣金额)/单价/课时数))
      let { course_name, hours, times,reduce, discount } = item;
      return `${item.course_name}(${(hours * times).toFixed(
        2
      )}课时、${reduce}元、${discount}%)`;
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>
