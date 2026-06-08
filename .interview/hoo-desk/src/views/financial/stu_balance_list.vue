<template>
  <div class="balance-setting">
    <div class="search-wrap">
        <!-- <v-mutex-check-bar
          label="类型"
          :checkList="balanceTypeList"
          @onChange="filterChange($event,'type_list')"
        ></v-mutex-check-bar> -->
        <!-- <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          :handleFunc="timeHandleFunc"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar> -->
        <v-search-bar placeholder="请输入关键词" @onSearch="toSearch"></v-search-bar>
        <v-filter-select
          label="校区筛选"
          :select-list="select_org_list"
          :is_trans_id="is_trans_id"
          defaultValue="0"
          :multiple="multiple"
          :showAll="showAll"
          @onChange="filterChange($event,'org_id_list')"
        ></v-filter-select>
        <v-range :startAmount="startAmount" :endAmount="endAmount" @outPutRange="outPutRange"></v-range>
    </div>
    <div class="pub-table-wrap">
      <el-row class="table-top-bar">
        <el-col>
          <el-button @click='toExport()'>数据导出</el-button>
        </el-col>
        <el-col type='flex'
                style="display:flex;align-items:center;justify-content:flex-end;">
          总余额：可用{{total}} 元
        </el-col>
      </el-row>
      <el-table :data="purseList"
                class="pub-table"
                v-loading='tableLoading'>
        <el-table-column prop='org_name' label="校区名称"></el-table-column>
        <!-- <el-table-column label="订单编号">
          <template slot-scope="scope">
            <el-button type='text'
                       @click='toOrder(scope.row)'
                       v-if="scope.row.order_sn">{{scope.row.order_sn}}</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column> -->
        <el-table-column label="学生姓名" prop='student_name'></el-table-column>
        <el-table-column label="当前余额" prop='balance'></el-table-column>
        <!-- <el-table-column label="金额">
          <template slot-scope="scope">
            <span v-if="scope.row.mode === '+'" style="color:#67c23a;">{{scope.row.mode}} {{scope.row.money}} 元</span>
            <span v-else style="color:#f56c6c;">{{scope.row.mode}} {{scope.row.money}} 元</span>
          </template>
        </el-table-column>
        <el-table-column label="日期" prop="created_date">
          <template slot-scope="scope">
            {{scope.row.created_date | formatToDate}}
          </template>
        </el-table-column> -->
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
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import range from "@/components/range";
import { getStudentBalanceList } from "@/api/student";
// import { getBalanceTypeList } from "@/api/student";
import { exportFile } from "@/api/exports";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      navSelect: "purse_list",
      total: 0,
      purseList: [],
      tableLoading: false,
      navList: [],
      datetime: ["0", "0"],
      is_trans_id: true,
      timeLabelList: [
        { label: "日", value: "day" },
        { label: "周", value: "week" },
        { label: "月", value: "month" }
      ],
    //   balanceTypeList: [],
      type_list: [],
      org_id_list: [],
      search: '',
      multiple: true,
      showAll: false,
      startAmount: 0,
      endAmount: 0,
      timeHandleFunc: {
        enable: true,
        func: function(val) {
          let startDate = new Date().setHours(0, 0, 0, 0);
          let endDate = new Date().setHours(23, 59, 59, 0);
          if (val === "week") {
            endDate = new Date(endDate);
            endDate = endDate.setDate(endDate.getDate() + 7);
          } else if (val === "month") {
            endDate = new Date(endDate);
            endDate = endDate.setMonth(endDate.getMonth() + 1);
          }
          return [startDate, endDate];
        }
      },
    };
  },
  mounted() {
    let nowDate = this.$getTimeStamp(new Date().toLocaleDateString(), 10)
    this.datetime[1] = nowDate
    this.getList();
    // this.getBalanceTypeList()
    this.$store.dispatch("setTopTitle", {
      title: "结算管理",
      des: "结算管理"
    });
    this.navList = this.$store.state.financial.nvaList;
  },
  methods: {
    outPutRange(val) {
      console.log('%cval','font-size:40px;color:pink;',val)
      if (Number(val['end_amount']) < Number(val['start_amount'])) {
        this.$message.error('请输入正确的金额范围')
      } else {
        this.startAmount = val.start_amount
        this.endAmount = val.end_amount
        this.getList()
      }
    },
    /**
    * toExport
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/04/30
     */
    toExport () {
      let obj = {
        org_id: localStorage.getItem("org_id"),
        user_id: localStorage.getItem("user_id"),
        // start_date: this.datetime[0],
        // end_date: this.datetime[1],
        org_id_list: this.org_id_list,
        search: this.search,
        min_money: this.startAmount,
        max_money: this.endAmount
      };
      exportFile({
        type: "student_balance.list",
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
          console.log("error", e);
          this.$message.error(e);
        });
    },

    /**
    * getBalanceTypeList
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/04/30
     */
    // getBalanceTypeList () {
    //   this.balanceTypeList = []
    //   getBalanceTypeList({})
    //   .then(res => {
    //     console.log('%cres','font-size:40px;color:pink;',res.data)
    //     res.data.forEach((item) => {
    //       let obj = {
    //         label: item.desc,
    //         value: item.type
    //       }
    //       this.balanceTypeList.push(obj)
    //     })
    //   })
    // },

    toSearch(e) {
      this.search = e
      this.getList()
    },
    filterChange(e, type) {
      console.log('%ce, type','font-size:40px;color:pink;',e, type)
      if (type !== "page") this.page = 1;
      if (type === 'type_list') {
        this[type] = e.split(',')
      } else {
        this[type] = e;
      }
      this.getList();
    },
    navChange(val) {
      this.$router.push({ name: val });
    },
    toOrder(item) {
      this.$router.push({
        name: "order_detail_new",
        query: { order_id: item.order_id }
      });
    },
    // 获取钱包列表
    getList() {
      this.tableLoading = true;
      getStudentBalanceList({
        page: this.page,
        size: this.size,
        // start_date: this.datetime[0],
        // end_date: this.datetime[1],
        org_id_list: this.org_id_list,
        search: this.search,
        min_money: this.startAmount,
        max_money: this.endAmount
      })
        .then(res => {
          console.log("获取钱包列表返回", res);
          this.purseList = res.data.list;
          this.total = res.data.total_balance;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    //翻页
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData",
      org_list: "common/getownOrgList",
    }),
    select_org_list() {
      let list = this.org_list
      list.forEach((item) => {
        item.id = item.org_id
        item.value = item.org_name
        item.label = item.org_name
      })
      return list
    }
  },
  components: {
    "v-mutex-check-bar": mutexCheckBar,
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-filter-select": FilterSelectBar,
    "v-range": range
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

.search-wrap
  padding 20px 30px
  border-bottom 10px solid #f6f8fb


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
.search-wrap >>> .el-input--medium .el-input__inner
  height 36px !important
  line-height 36px
.search-wrap >>> .el-select .el-input .el-select__caret
  display flex
  justify-content center
  align-items center
.search-wrap >>> .index-content
  width 414px !important
.search-wrap >>> .search-bar
  margin-bottom 16px
</style>
