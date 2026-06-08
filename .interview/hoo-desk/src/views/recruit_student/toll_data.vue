<template>
  <div>
   <v-table-wrap
      :page="page"
      :total="orderTotal"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      placeholder="姓名、订单号、科目、学期搜索"
      @onSearch="filterChange($event,'search')"
    >
      <el-button slot="buttons" type="primary" @click="toCreatStudent">快速缴费</el-button>
      <el-button slot="buttons" @click="toImportOrders">批量导入订单</el-button>
    <!-- showSearch -->
      <div slot="searchItems" class="search-wrap">
        <!-- <v-filter-date-bar
          label="筛选时间"
          :date-list="timeLabelList"
          @onChange="filterChange($event,'datetime')"
        ></v-filter-date-bar>
        <v-filter-select-bar
          label="状态"
          :select-list="statusList"
          @onChange="filterChange($event,'status')"
        ></v-filter-select-bar>-->
        <v-search-bar
          label="搜索名称"
          placeholder="请输入姓名、订单号、学期或科目搜索"
          :width="'300px'"
          :block="'inline-block'"
          @onSearch="filterChange($event,'search')"
        ></v-search-bar>


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
        <v-mutex-check-bar
          label="状态"
          :max="mutexCheckMax"
          :checkList="statusList"
          @onChange="filterChange($event,'status')"
        ></v-mutex-check-bar>
        <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          :handleFunc="timeHandleFunc"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar>
        <!-- <v-search-bar placeholder="请输入分校名" @onSearch="toSearch"></v-search-bar> -->
        <!-- <v-filter-select
          label="校区筛选"
          :select-list="select_org_list"
          :is_trans_id="is_trans_id"
          defaultValue="0"
          @onChange="filterChange($event,'is_bind')"
        ></v-filter-select> -->
      </div>
      <template slot="table_title">缴费订单</template>
      <el-button @click="postDeliver" slot="table_btns">一键审核</el-button>
      <el-button @click="batchEndClass" type="primary" slot="table_btns" v-if="show_close_course">批量结课</el-button>
      <el-button @click="multiSelect" type="primary" slot="table_btns" v-if="show_close_course">订单全选</el-button>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{orderTotal}}</i>份订单
      </div>
      <el-table
        ref="multipleTable"
        :data="orderList"
        tooltip-effect="dark"
        v-loading="tableLoading"
        class="pub-table"
        slot="table"
      >
        <el-table-column width="55">
          <template slot-scope="scope">
            <!-- <el-checkbox
              v-if="scope.row.lock == 0
            &&(parseFloat(scope.row.received_total) >  parseFloat(scope.row.paid_amount))
            && scope.row.is_del == 0
            && scope.row.apply_diff == 1"
              v-model="scope.row.isChecked"
              :checked="scope.row.isChecked"
              style="margin-left: 5px; marin-right:200px;"
              @change="ischeck(scope.row)"
            ></el-checkbox>
            <span
              v-if="scope.row.lock != 0
            ||(parseFloat(scope.row.received_total) <= parseFloat(scope.row.paid_amount))
            || scope.row.is_del != 0 || scope.row.apply_diff == 0"
              style="margin-left: 10px;"
            >/</span> -->
            <el-checkbox
            v-if="scope.row.can_close_course === 1"
            v-model="scope.row.isChecked"
            :checked="scope.row.isChecked"
            style="margin-left: 5px; marin-right:200px;"
            @change="ischeck(scope.row)"
            >
            </el-checkbox>
            <span
            v-else-if="scope.row.can_close_course === 0"
            style="margin-left: 10px;"
            ></span>
          </template>
        </el-table-column>
        <el-table-column type="index"></el-table-column>
        <el-table-column prop="order_sn" label="订单编号"  width="150">
           <template slot-scope="scope">
              <el-button type="text" prop="order_sn" @click="handleClickNew(scope.row)">{{scope.row.order_sn}}</el-button>
              <span @click="handleClickNew(scope.row)" style=""></span>
          </template>
        </el-table-column>
        <el-table-column prop="order_title" show-overflow-tooltip label="报名课程" width="250">
          <template slot-scope="scope">
            <div v-for='(i, k) in scope.row.course_name' :key="k">
              {{i}}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="receivable_total" label="应收金额" show-overflow-tooltip></el-table-column>
        <el-table-column prop="diff_amount" label="应收差额" show-overflow-tooltip></el-table-column>
        <el-table-column label="时间" prop="created_date" show-overflow-tooltip>
          <template slot-scope="scope">{{scope.row.created_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column label="创建人" show-overflow-tooltip prop="created_user"></el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" width="220" fixed="right">
          <template slot-scope="scope">
            <div v-if="scope.row.is_del == 0">
              <el-button type="text" @click="handleClickNew(scope.row)">查看详情</el-button>
              <el-button
                v-if="scope.row.received_total == 0"
                @click="cancelOrder(scope.row)"
                type="text"
              >删除</el-button>
              <el-button
                type="text"
                v-if="Number(scope.row.diff_amount)>0"
                @click="handleClickNew(scope.row)"
              >补交尾款</el-button>
            </div>
            <div v-if="scope.row.is_del == 1">订单已注销</div>
          </template>
        </el-table-column>
      </el-table>
      <!-- <el-button slot="table-footer" style="margin: 10px 0 10px 10px;" @click="postDeliver">一键审核</el-button> -->
    </v-table-wrap>
    <!-- 批量结课-->
    <el-dialog title="批量结课" :visible.sync="batchEndCourseShow" :close-on-click-modal="false">
      <div class="list-wrap">
        <div class="table-info">
           结课课程：{{mutiArr.length}}个，结课金额：{{mutiArrMoney}}
        </div>
        <el-table
          ref="multipleTable"
          :data="mutiArr"
          tooltip-effect="dark"
          class="pub-table"
        >
          <el-table-column prop="order_sn" label="订单编号" width="150"></el-table-column>
          <el-table-column prop="subject_name" label="科目"></el-table-column>
          <el-table-column prop="course_name" label="课程" width="150"></el-table-column>
          <el-table-column prop="course_term" label="学期"></el-table-column>
          <el-table-column prop="student_name" label="学员姓名" align="center"></el-table-column>
          <el-table-column prop="student_name" label="剩余总课时" align="center">
            <template slot-scope="scope">
              {{getLessTime(scope.row)}}/{{getTime(scope.row)}}
              <!-- {{scope.row.less_times*scope.row.hours}}/{{scope.row.times*scope.row.hours}} -->
            </template>
          </el-table-column>
          <el-table-column label="调整后课时" align="center">
            <template >
              0
            </template>
          </el-table-column>
          <!-- <el-table-column prop="student_name" label="调整后课时"></el-table-column> -->
          <el-table-column prop="refund_fee" label="结课金额" align="center"></el-table-column>
        </el-table>
      </div>
      <div class="input-wrap" style="margin-bottom:10px;">
        <div style="margin-bottom:10px;" class="input-title">结课原因</div>
        <el-input
          type="textarea"
          :rows="5"
          placeholder="请输入结课原因"
          v-model="end_class_reason">
        </el-input>
      </div>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="confimEndClass">确认结课</el-button>
        <el-button @click="endClassShowClose">取消</el-button>
      </div>
    </el-dialog>
    <v-progress :progressShow="progressShow" :percentage="percentage"/>
  </div>
</template>

<script>
import tableTemplate from "@/components/listViewTemplate";
import { getOrderList, deliverList, delOrder, easyPost } from "@/api/order";
import { reduceCourseTime } from "@/api/course_control";
import filterDateBar from "@/components/top_box/filter_date_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import searchNewBar from "@/components/top_box/search_new_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import progress from "@/components/progress"
import { mapGetters } from 'vuex';
export default {
  data() {
    return {
      show_close_course: false,
      statusList: [
        { label: "已付清", value: "2", id: "2" },
        { label: "未付清", value: "1", id: "1" },
        { label: "未交款", value: "0", id: "0" }
      ],
      status: "",
      org_id: 0,
      search: "",
      checkList: "",
      orderTotal: 0,
      page: 1, //分页每页显示10条
      size: 10,
      orderList: [],
      multipleSelection: [],
      id_list: [],
      timeBtnValue: "all",
      start_date: "",
      end_date: "",
      datetime: [],
      tableLoading: false,
      // timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      datetime: ["", ""],
      is_trans_id: true,
      timeLabelList: [
        { label: "日", value: "day" },
        { label: "周", value: "week" },
        { label: "月", value: "month" }
      ],
      isMulti: false,//是否全选
      mutiArr: [],
      mutiArrToSend: [],//接口传送的结课课程数组
      batchEndCourseShow: false,
      end_class_reason: '',
      progressShow: false,
      course_term_list:[],//筛选项-学期
      subject_name_list:[],//筛选项-科目
      mutexCheckMax: 1,//筛选项-最大可选数量
      currentEndClassAmount: 0,//当前已结课数量
      percentage: 0,
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
    let start_date = new Date().setHours(0, 0, 0, 0) - 60 * 60 * 24 * 365 * 1000;
    let end_date = new Date().setHours(23, 59, 59, 0);
    this.datetime = [start_date / 1000, end_date / 1000];
    this.datetime = [start_date / 1000, end_date / 1000];
    let powerList = this.user.power_list;
    if ((powerList.findIndex(item => item === 'batch_close_course')) !== -1) {
      this.show_close_course = true
    } else {
      this.show_close_course = false
    }
  },
  activated(){
    this.mutiArr = []
    this.orderList.forEach((item) => {
      item.is_checked = false
    })
    // 新版不请求
    if(!this.isNewType) this.init();
    // 批量导入订单后 点击保存跳转进入 传入temp值 进行重新获取订单数据
    if(this.$route.query.temp) this.init();
    let powerList = this.user.power_list;
    if ((powerList.findIndex(item => item === 'batch_close_course')) !== -1) {
      this.show_close_course = true
    } else {
      this.show_close_course = false
    }
  },
  methods: {
    /**
    * endClassShowClose
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/05/08
     */
    endClassShowClose () {
      this.batchEndCourseShow = false
      this.mutiArr = []
    },

    /**
    * 确认结课
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/04/27
     */
    confimEndClass () {
      this.progressShow = true
      this.currentEndClassAmount = 0
      this.percentage = 0
      let progressArr = []
      this.mutiArrToSend.forEach((item, index) => {
        let endClassObj = {
          dec_reason: this.end_class_reason,
          order_id: item[0].order_id,
          from: "batch_close_course",
          course_list: [],
        }
        item.forEach((e) => {
          endClassObj.course_list.push(e)
        })
        let progressItem = this.singleEndClass(endClassObj, index)
        progressArr.push(progressItem)
      })
      Promise.all(progressArr).then((res) => {
        this.progressShow = false
        this.$message.success('结课成功')
        this.mutiArr = []
        setTimeout(() => {
          this.batchEndCourseShow = false
          this.init()
        }, 0)
      }).catch(err => {
        this.$message({
              message: err,
              type: 'error',
              duration: 5000,
            })
            this.progressShow = false
            this.currentEndClassAmount = 0
            this.percentage = 0
            this.mutiArr = []
      })
    },
    singleEndClass(endClassObj, index) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // endClassObj.course_list[0].times = 0
          endClassObj.course_list.forEach((item) => {
            item.times = 0
          })
          endClassObj.course_list[0].close_times = endClassObj.course_list[0]['less_times'] * endClassObj.course_list[0]['hours']
          reduceCourseTime(endClassObj)
          .then(res => {
            this.currentEndClassAmount ++
            resolve(true)
          })
          .catch(err => {
            reject(err)
          })
        }, 2000)
      })
    },
    /**订单单选 */
    ischeck(data) {
      data.can_close_course_list = this.$createIterator(data.can_close_course_list)//迭代器
      // if (data.isChecked == true) {
      //   for (let item of data.can_close_course_list) {
      //     item.order_sn = data.order_sn
      //     this.mutiArr.push(item)
      //   }
      // } else {
      //   this.mutiArr.forEach((item, index) => {
      //     if (item.order_sn === data.order_sn) {
      //       this.mutiArr.splice(index, 1)
      //     }
      //   })
      this.isMulti = false
      // }
    },
    /**
    * 订单多选
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/04/27
     */
    multiSelect () {
      this.mutiArr = []

      //已经有单选的情况，多选先清空
      this.orderList.forEach((item) => {
        if (item.isChecked) {
          this.isMulti = true
          return
        }
      })
      for (let i = 0; i < this.orderList.length; i++) {
        if (this.orderList[i].can_close_course === 1) {
          if (!this.isMulti) {
            this.$set(this.orderList[i], 'isChecked', true)
            // for(let item of this.orderList[i].can_close_course_list) {
            //   item.order_sn = this.orderList[i].order_sn
            //   this.mutiArr.push(item)
            // }
          } else {
            this.$set(this.orderList[i], 'isChecked', false)
          }
        }
      }
      this.isMulti = !this.isMulti
    },

    /**
    * 批量结课按钮点击
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/04/27
     */
    batchEndClass () {
      let noclass = true
      let chooseList = []
      this.orderList.forEach((item, index) => {
        if (item.isChecked) {
          noclass = false
          if (Array.isArray(item.can_close_course_list)) {
            chooseList[index] = []
            item.can_close_course_list.forEach((e) => {
              e.order_sn = item.order_sn
              // e.times = 0
              e.close_times = e.less_times * e.hours
              chooseList[index].push(e)
            })
          } else {
            chooseList[index] = []
            for(let e of item.can_close_course_list) {
              e.order_sn = item.order_sn
              // e.times = 0
              e.close_times = e.less_times * e.hours
              chooseList[index].push(e)
            }
          }
        }
      })
      if (noclass) {
        this.$message.error('未选择需结课的课程')
      } else {
        chooseList.forEach((item) => {
          item.forEach((e) => {
            this.mutiArr.push(e)
          })
        })
        this.mutiArrToSend = chooseList
        // console.log('%cthis.mutiArr1','font-size:40px;color:pink;',this.mutiArr)
        // console.log('%cthis.mutiArr2','font-size:40px;color:pink;',this.mutiArrToSend)
        this.batchEndCourseShow = true
      }
    },
    toImportOrders() {
      // 批量导入订单
      // this.$router.push({ path: "/recruit_student/importOrders" });
      this.$router.push({ path: "/recruit_student/import_order_preview/import_order_preview" });
    },
    filterChange(val, type) {
      if (type === 'course_term_list' || type === 'subject_name_list') {
        val = val.split(",")
      }
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    handleClickNew(data, href) {
      this.$router.push({
        name: "order_detail_new",
        query: { order_id: data.order_id }
      });
    },
    init() {
      let obj = {
        page: this.page,
        count: this.size,
        status: this.status,
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        course_term_list: this.course_term_list,
        subject_name_list: this.subject_name_list,
      };
      this.tableLoading = true;
      getOrderList(obj)
        .then(res => {
          let result = res.data;
          this.orderTotal = parseInt(result.count);
          this.orderList = result.list;
          for (let i = 0; i < this.orderList.length; i++) {
            this.orderList[i].orderCourse = this.orderList[i].order_title.split(',')
            this.orderList[i].can_close_course_list = this.$createIterator(this.orderList[i].can_close_course_list)
            this.$set(this.orderList[i], "isChecked", false);
          }
          this.isMulti = false
          this.tableLoading = false;
        })
        .catch((e) => {
          this.tableLoading = false;
        });
    },
    toCreatStudent() {
      this.$router.push({
        path: "/recruit_student/creat_student_new"
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
    //    数组查重
    isRepeat(data) {
      var arr = data,
        i,
        j,
        len = arr.length;
      for (i = 0; i < len; i++) {
        for (j = i + 1; j < len; j++) {
          if (arr[i] == arr[j]) {
            arr.splice(j, 1);
            len--;
            j--;
          }
        }
      }
      return arr;
    },
    //      提交订单
    postDeliver() {
      let obj = {
        org_id: this.org_id,
        page: 1,
        size: 20,
        search: this.search,
        closing_date: this.datetime[1],
        payment: ""
      };

      easyPost(obj)
        .then(res => {
          let result = res.data;
          let orderTotal = parseInt(result.count);

          if (orderTotal > 0) {
            this.$router.push({
              name: "easy_post"
            });
          } else {
            this.$message.warning("暂无可提交金额！");
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    cancelOrder(rows) {
      let order_id = rows.order_id;
      this.$confirm("此操作将永久撤销订单, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delOrder({ order_id: order_id });
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.init();
          }
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    }
  },
  components: {
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-search-new-bar": searchNewBar,
    "v-table-wrap": tableTemplate,
    // "v-filter-select-bar": filterSelectBar,
    "v-filter-select": FilterSelectBar,
    "v-filter-date-bar": filterDateBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-progress":　progress
  },
  computed: {
    ...mapGetters({
      user:'user',
      isNewType: "common/getSystemType",
      searchData: "common/getSearchData",
      org_list: "common/getownOrgList",
    }),
    mutiArrMoney() {
      let amount = 0
      this.mutiArr.forEach((item) => {
        amount += item.refund_fee
      })
      return amount
    },
    select_org_list() {
      let list = this.org_list
      list.forEach((item) => {
        item.id = item.org_id
        item.value = item.org_name
        item.label = item.org_name
      })
      return list
    },
    getLessTime() {
      return (data) => {
        let returnNum = parseInt(data.less_times) * parseInt(data.hours)
        return returnNum
      }
    },
    getTime() {
      return (data) => {
        let returnNum = parseInt(data.times) * parseInt(data.hours)
        return returnNum
      }
    },
  },
  watch: {
    currentEndClassAmount() {
      let endClassAmount = this.mutiArr.length
      let currentPercentage = parseInt((this.currentEndClassAmount / endClassAmount) * 100)
      this.percentage = currentPercentage
    }
  }
};
</script>
<style lang="stylus" scoped>
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

.search-wrap >>> .index-label
  margin-left 0px !important
.search-wrap >>> .el-input--medium .el-input__inner
  height 30px
  line-height 30px
.search-wrap >>> .el-select .el-input .el-select__caret
  display flex
  justify-content center
  align-items center
.search-wrap >>> .index-content
  width 414px !important
.search-wrap >>> .search-bar
  margin-bottom 10px
</style>
