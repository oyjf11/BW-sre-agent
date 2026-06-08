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
    <div class="search-wrap">
        <v-mutex-check-bar
          label="科目"
          :checkList="searchData.subject"
          @onChange="filterChange($event,'subject_name_list')"
        ></v-mutex-check-bar>
        <v-mutex-check-bar
          label="学期"
          :checkList="searchData.term"
          @onChange="filterChange($event,'course_term_list')"
        ></v-mutex-check-bar>
        <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          :handleFunc="timeHandleFunc"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar>
        <v-search-bar placeholder="请输入关键字" @onSearch="toSearch"></v-search-bar>
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
    <div class="pub-table-wrap">
      <el-table v-loading='tableLoading'
                :data="listData"
                class='pub-table'>
        <el-table-column prop='org_name'
                         label='分校名称'></el-table-column>
        <el-table-column prop='order_sn'
                         label='订单编号'>
          <template slot-scope="scope">
            <el-button type='text'
                       v-if='scope.row.order_sn'
                       @click='toOrder(scope.row)'>{{scope.row.order_sn}}</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="student_name"
                         label='学生姓名'></el-table-column>
        <el-table-column prop='course_name'
                         label='课程名称'></el-table-column>
        <el-table-column prop='actual_refund_fee'
                         label='结算金额'></el-table-column>
        <el-table-column label='操作人' prop='user_name'></el-table-column>
        <el-table-column label='结课原因' prop='remark'></el-table-column>
        <el-table-column label='结课时间'>
          <template slot-scope="scope">{{scope.row.updated_date | formatToDate('Y-M-D h:m')}}</template>
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
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
// import { getFinishList } from "@/api/balance";
import { closeCourseHistory } from "@/api/order";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      navSelect: "finish_list",
      listData: [],
      tableLoading: false,
      navList:[],
      datetime: ["", ""],
      is_trans_id: true,
      timeLabelList: [
        { label: "日", value: "day" },
        { label: "周", value: "week" },
        { label: "月", value: "month" }
      ],
      subject_name_list: [],
      course_term_list: [],
      org_id_list: [],
      search: '',
      multiple: true,
      showAll: false,
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
  created() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "结算管理",
      des: "结算管理"
    });
    this.navList = this.$store.state.financial.nvaList;
  },
  methods: {
    toSearch(e) {
      this.search = e
      this.getList()
    },
    filterChange(e, type) {
      console.log('%ce, type','font-size:40px;color:pink;',e, type)
      if (type !== "page") this.page = 1;
      if (type === 'subject_name_list' || type === 'course_term_list') {
        if (e === '') {
          this[type] = []
        } else {
          this[type] = e.split(',')
        }
      } else {
        this[type] = e
      }
      // this[type] = e;
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
    // 获取申请提现列表
    getList() {
      this.tableLoading = true;
      closeCourseHistory({ 
        page: this.page, 
        count: this.size, 
        from:"kehan",
        subject_name_list: this.subject_name_list,
        course_term_list: this.course_term_list,
        org_id_list: this.org_id_list,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        search: this.search
        })
        .then(res => {
          console.log("获取提现申请列表返回", res);
          this.listData = res.data.list;
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
    line-height: 36px;
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
