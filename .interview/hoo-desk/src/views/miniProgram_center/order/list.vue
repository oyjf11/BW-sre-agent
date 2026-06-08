<template>
  <div>
    <v-table-wrap :page='page'
      :total="orderTotal"
      showSearch
      placeholder="请输入用户名称"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'pageCount')"
    >
      <template slot="searchItems">
        <div class="search-wrap">
          <v-time-bar
            :all="false"
            :time="datetime"
            :timeList="timeLabelList"
            @onChange="filterChange($event,'datetime')"
          ></v-time-bar>
          <v-radio-bar
            radio="2"
            :all="false"
            label="支付状态"
            @onChange="filterChange($event,'is_pay')"
            :radioList="payList"
          ></v-radio-bar>
          <v-filter-select
            label="校区筛选"
            :select-list="select_org_list"
            :is_trans_id="is_trans_id"
            defaultValue="0"
            :multiple="multiple"
            :showAll="showAll"
            @onChange="filterChange($event,'org_id_list')"
          ></v-filter-select>
        </div>
      </template>
      <template slot="table_title">订单列表</template>
      <el-button slot="table_btns" type="primary" @click="exportOrder">导出订单</el-button>
      <div slot="table_count" class="count">
        当前订单：共计
        <i style="color:#f86b6e;">{{orderTotal}}</i>份订单
      </div>
      <el-table
        slot="table"
        ref="multipleTable"
        class="pub-table"
        v-loading="tableLoading"
        :data="orderList"
      >
        <el-table-column type="index" width="55"></el-table-column>
        <el-table-column prop="order_title" label="报名课程"></el-table-column>
        <el-table-column prop="subject_name" label='科目'></el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="receivable_total" label="应收金额" show-overflow-tooltip></el-table-column>
        <el-table-column label="开始上课时间" prop="created_date" show-overflow-tooltip>
          <template slot-scope="scope">{{scope.row.created_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column label="校区">
          <template slot-scope="scope">
            {{scope.row.org_name}}
            <el-button
              type="text"
              v-if="scope.row.can_change_org / 1 ===1"
              @click="openOrgDialog(scope.row)"
            >修改</el-button>
          </template>
        </el-table-column>
        <el-table-column label="推荐人">
          <template slot-scope="scope">{{scope.row.reference ? scope.row.reference : "无"}}</template>
        </el-table-column>
        <el-table-column label="订单状态" show-overflow-tooltip>
          <template slot-scope="scope">
            <span v-if="scope.row.diff_amount > 0">未支付</span>
            <span v-if="scope.row.diff_amount == 0">已支付</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间">
          <template slot-scope="scope">{{scope.row.created_date | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button @click="handleClick(scope.row)" type="text" v-if="scope.row.is_del == 0 && is_pay!=1">编辑</el-button>
            <el-button
              @click="handleDel(scope.row)"
              type="text"
              v-if="scope.row.diff_amount == 0&&scope.row.is_del == 0"
            >退款</el-button>
            <span v-if="scope.row.is_del == 1 && scope.row.diff_amount >0">订单已取消</span>
            <div v-if="scope.row.is_del == 1 && scope.row.diff_amount <=0">订单已退款</div>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog
      class="miniprogram-del-order"
      title="订单退款"
      :visible.sync="delDialogShow"
      @close="closeDialog"
    >
      <el-row type="flex">
        <el-col :span="4" class="label" style="text-align:right">备注</el-col>
        <el-col :span="14" :offset="1">
          <el-input v-model="delRemark" placeholder="请输入备注"></el-input>
        </el-col>
      </el-row>
      <div slot="footer" class="dialog-btn-bar">
        <el-button @click="toDel" type="primary">确定</el-button>
        <el-button @click="delDialogShow = false">取消</el-button>
      </div>
    </el-dialog>
    <el-dialog
      title="修改校区"
      width="500px"
      class="org-dialog"
      :visible.sync="orgDialogShow"
      @close="closeOrgDialog"
    >
      <el-row type="flex">
        <el-col :span="4" class="label">选择校区</el-col>
        <el-col :span="20">
          <el-select
            style="width:100%"
            class="org-select"
            v-model="updateOrg.org_id"
            placeholder="选择校区"
            filterable
          >
            <el-option
              v-for="item in orgList"
              :key="item.org_id"
              :label="item.org_name"
              :value="item.org_id"
            ></el-option>
          </el-select>
        </el-col>
      </el-row>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="updateOrgFunc">修改</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getOrderList, deliverList, delOrder } from "@/api/order";
import { updateOrderOrg, exportOrder } from "@/api/miniProgram_center";
import { exportFile } from "@/api/exports"
import { mapState, mapGetters } from "vuex";
import searchBar from "@/components/top_box/search_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import timeBar from "@/components/top_box/time_bar";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    let startTime = new Date().setHours(0, 0, 0, 0) - 60 * 60 * 24 * 365 * 1000;
    let endTime = new Date().setHours(23, 59, 59, 0);
    return {
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      is_pay: "2",
      payList: [
        { label: "已支付", value: "2" },
        { label: "未支付", value: "1" },
        { label: "已退款", value: "3" },
        { label: "已取消", value: "4" }
      ],
      org_id: 0,
      search: "",
      checkList: "",
      orderTotal: 0,
      page: 1, //分页每页显示10条
      pageCount: 10,
      orderList: [],
      datetime: [startTime / 1000, endTime / 1000],
      delDialogShow: false,
      delRemark: "",
      delId: null,
      updateOrg: {
        org_id: null,
        info: null
      },
      orgDialogShow: false,
      tableLoading: false,
      is_trans_id: true,
      multiple: true,
      showAll: false,
      org_id_list: []//校区数组
    };
  },
  activated() {
    this.init();
  },
  computed: {
    ...mapGetters({orgList:"common/getownOrgList"}),
    select_org_list() {
      let list = this.orgList
      list.forEach((item) => {
        item.id = item.org_id
        item.value = item.org_name
        item.label = item.org_name
      })
      return list
    }
  },
  components: {
    "v-search-bar": searchBar,
    "v-time-bar": timeBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate,
    "v-filter-select": FilterSelectBar,
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    openOrgDialog(item) {
      this.orgDialogShow = true;
      this.updateOrg.org_id = item.org_id;
      this.updateOrg.info = item;
    },
    closeOrgDialog() {
      this.orgDialogShow = false;
      this.updateOrg.org_id = null;
      this.updateOrg.info = null;
    },
    exportOrder() {
      let org_id = this.$route.query.org_id;
      this.org_id = org_id;
      let obj = {
        org_id: org_id,
        page: this.page,
        count: this.pageCount,
        status: "",
        is_pay: this.is_pay,
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        type: 1,
        org_id_list: this.org_id_list,
      };
      exportFile({
        type: "hot_course_order.list",
        query_params: JSON.stringify(obj)
      })
        .then(res => {
          this.$message.success("创建导出任务成功");
          let timer = setTimeout(() => {
            window.open("/saas/export_control/file_list");
            clearTimeout(timer);
          }, 500);
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    updateOrgFunc() {
      let info = this.updateOrg.info;
      let data = {
        order_id: info.order_id,
        org_id: this.updateOrg.org_id,
        old_org_id: info.org_id,
        stu_id: info.stu_id,
        student_name: info.student_name
      };
      updateOrderOrg(data)
        .then(res => {
          console.log(res, "修改校区成功");
          this.$message.success("修改校区成功");
          this.init();
          this.orgDialogShow = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("修改校区失败");
        });
    },
    timeChange(date) {
      this.datetime = date;
      this.page = 1;
      this.init();
    },
    toSearch(val) {
      this.search = val;
      this.page = 1;
      this.init();
    },
    // 课程编辑
    handleClick(data) {
      console.log(data);
      this.$router.push({
        path: "/recruit_student/order_detail_new?order_id=" + data.order_id
      });
    },
    init() {
      let org_id = this.$route.query.org_id;
      this.org_id = org_id;
      let obj = {
        org_id: org_id,
        page: this.page,
        count: this.pageCount,
        status: "",
        is_pay: this.is_pay,
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        type: 1,
        org_id_list: this.org_id_list,
      };
      this.tableLoading = true;
      getOrderList(obj)
        .then(res => {
          let result = res.data;
          this.orderTotal = parseInt(result.count);
          this.orderList = result.list;
          for (let i = 0; i < this.orderList.length; i++) {
            this.$set(this.orderList[i], "isChecked", false);
          }
          this.tableLoading = false;
        })
        .catch(error => {
          this.tableLoading = false;
          console.log(error);
        });
    },
    toCreatStudent() {
      this.$router.push({
        path: "/recruit_student/creat_student"
      });
    },
    closeDialog() {
      this.delDialogShow = false;
      this.delId = null;
      this.delRemark = "";
    },
    toDel() {
      if (!this.delRemark) {
        this.$message.error("请输入备注");
        return;
      }
      this.$confirm("是否确定退款?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delOrder({ order_id: this.delId, remark: this.delRemark });
        })
        .then(res => {
          this.$message.success("订单退款成功");
          this.delDialogShow = false;
          this.init();
        })
        .catch(e => {
          if (e != "cancel") {
            if (e == "已提交交款不能删除") {
              this.$message.error("已提交审核，不能退款");
            } else {
              this.$message.error(e);
            }
          }
          console.log(e);
        });
    },
    handleDel(rows) {
      this.delDialogShow = true;
      this.delId = rows.order_id;
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.miniprogram-del-order
  .btn-bar
    margin-top: 20px;
    justify-content: center;
.org-dialog
  line-height: 36px;
  .submit-btn
    margin-top: 20px;
    text-align: center;

// .search-wrap
//   padding 20px 30px
//   border-bottom 10px solid #f6f8fb


.search-wrap >>> .filter-label
    -webkit-box-flex: 0;
    -webkit-flex: 0 0 70px;
    -ms-flex: 0 0 70px;
    flex: 0 0 70px;
    width: auto;
    font-size: 14px;
    text-align: left;
    margin-right: 10px;
    line-height: 30px;
    display flex
    align-items center

.search-wrap >>> .index-label
  margin-left 0px !important
.search-wrap >>> .el-select .el-input .el-select__caret
  display flex
  justify-content center
  align-items center
.search-wrap >>> .index-content
  width 414px !important
.search-wrap >>> .search-bar
  margin-bottom 16px
</style>
