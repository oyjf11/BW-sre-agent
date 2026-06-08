<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      showSearch
      placeholder="校区、学员、学期搜索"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <template slot="searchItems">
        <v-mutex-check-bar
          label="科目"
          :checkList="searchData.subject"
          @onChange="filterChange($event,'subject')"
        ></v-mutex-check-bar>
        <v-mutex-check-bar
          label="学期"
          status="1"
          :checkList="searchData.term"
          @onChange="filterChange($event,'term')"
        ></v-mutex-check-bar>
        <!-- <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar>-->
        <v-radio-bar
          :all="false"
          label="预警"
          :radio="JumpWarning"
          @onChange="filterChange($event,'warning')"
          :radioList="warningList"
        ></v-radio-bar>
        <v-radio-bar
          label="排班状态"
          :radio="JumpArrange"
          @onChange="filterChange($event,'hasClass')"
          :radioList="classStatusList"
        ></v-radio-bar>
      </template>
      <template slot="table_title">预收表</template>
      <el-button slot="table_btns" @click="exportList">导出列表</el-button>
      <el-table slot="table" v-loading="tableLoading" class="pub-table" :data="listData">
        <el-table-column prop="org_name" label="校区名称"></el-table-column>
        <el-table-column label="订单编号" width="160px">
          <template slot-scope="scope">
            <el-button type="text" @click="toOrder(scope.row)">{{scope.row.order_sn}}</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="student_name" label="学员名称"></el-table-column>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column label="班级名称">
          <template slot-scope="scope">
            <div class="can-click" @click="toAddClass(scope.row)">{{scope.row.class_name || '待分班'}}</div>
          </template>
        </el-table-column>
        <el-table-column prop="times" label="购买课时">
          <template slot-scope="scope">{{scope.row.times * scope.row.hours |toFixed}}</template>
        </el-table-column>
        <el-table-column prop="price" label="课程单价"></el-table-column>
        <el-table-column label="学费总额">
          <template slot-scope="scope">{{scope.row.receivable - scope.row.sundry_fees | fixed(2)}}</template>
        </el-table-column>
        <el-table-column label="已收合计" prop="received"></el-table-column>
        <el-table-column label="未交学费" prop="diff_amount"></el-table-column>
        <el-table-column label="课消课时">
          <template slot-scope="scope">
            <span
              class="blue-text c-pointer"
              @click="jumpViewClassRecord(scope.row)"
            >{{scope.row.used_times}}</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余课时" prop="surplus_times">
          <!-- <template slot-scope='scope'>
            {{ (scope.row.times * scope.row.hours) - ((scope.row.times - scope.row.surplus_times)*scope.row.hours) | fixed(2) }}
          </template>-->
        </el-table-column>
        <el-table-column label="累计课消金额" prop="consume_amount"></el-table-column>
        <el-table-column label="剩余学费">
          <template
            slot-scope="scope"
          >{{ scope.row.received - scope.row.consume_amount | fixed(2) }}</template>
        </el-table-column>
        <!-- <el-table-column label="学杂费" prop="sundry_fees"></el-table-column> -->
      </el-table>
    </v-table-wrap>
    <v-choose-class
      :courseInfo="bindCourseInfo"
      :dialog="showClassChoose"
      @addSuccess="addClassSuccess"
      @close="showClassChoose = false"
      :oneToOne="is_one_to_one"
    ></v-choose-class>
  </div>
</template>


<script>
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import { getRevenueList, exportRevenueList } from "@/api/student_control";
import tableTemplate from "@/components/listViewTemplate";
import { AttrList } from "@/api/operations_center";
import chooseClass from "../../recruit_student/order_details/choose_class";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      datetime: [],
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      warningList: [
        { label: "不限", value: "-1" },
        { label: "剩余课时少于5", value: "5" }
      ],
      classStatusList: [
        { label: "未排班", value: "1" },
        { label: "已排班", value: "2" }
      ],
      hasClass: "",
      warning: "-1",
      tableLoading: false,
      listData: [],
      subject: "",
      search: "",
      term: "",
      page: 1,
      size: 10,
      count: 0,
      showClassChoose: false,
      bindCourseInfo: null,
      is_one_to_one: "",
      JumpArrange: "-1",
      JumpWarning: ""
    };
  },
  created() {
    let start_date = new Date(new Date().setDate(1)).setHours(0, 0, 0, 0);
    let end_date = new Date().setHours(23, 59, 59, 0);
    this.datetime = [start_date / 1000, end_date / 1000];
    let jumpQuery = this.$route.query;
    if (jumpQuery.label) {
      switch (jumpQuery.label) {
        case "预警":
          this.warning = jumpQuery.warningId;
          this.hasClass = "";
          this.JumpWarning = jumpQuery.warningId;
          this.JumpArrange = "all";
          break;
        case "排班状态":
          this.warning = -1;
          this.hasClass = jumpQuery.ArrangeId;
          this.JumpArrange = jumpQuery.ArrangeId;
          this.JumpWarning = "-1";
          break;
      }
    } else {
      this.JumpWarning = "-1";
      this.JumpArrange = "all";
      this.warning = -1;
      this.hasClass = "";
    }
  },
  activated() {
    // console.log(sessionStorage.jumpData.ArrangeId);
    // let jumpData=JSON.parse(sessionStorage.jumpData)
    let jumpQuery = this.$route.query;
    console.log(jumpQuery);

    if (jumpQuery.label) {
      switch (jumpQuery.label) {
        case "预警":
          this.warning = jumpQuery.warningId;
          this.hasClass = "";
          this.JumpWarning = jumpQuery.warningId;
          this.JumpArrange = "all";
          break;
        case "排班状态":
          this.warning = -1;
          this.hasClass = jumpQuery.ArrangeId;
          this.JumpArrange = jumpQuery.ArrangeId;
          this.JumpWarning = "-1";
          break;
      }
    } else {
      this.JumpWarning = "-1";
      this.JumpArrange = "all";
      this.warning = -1;
      this.hasClass = "";
    }
    // 新版不请求
    if (!this.isNewType) {
      this.getList();
    }
  },
  filters: {
    toFixed(val) {
      return (val / 1).toFixed(2);
    }
  },
  methods: {
    /**
     * jumpViewClassRecord
     * 跳转查看上课记录页面
     * @param  Array     {row}
     * Created by preference on 2019/08/14
     */
    jumpViewClassRecord(item) {
      console.log("跳转查看上课记录页面", item);
      // this.$router.push({
      //   path: "/recruit_student/revenue_list/view_class_record",
      //   query: {
      //     order_course_id: row.order_course_id
      //   }
      // })
      this.$router.push({
        name: "lesson_schedule_student",
        query: {
          order_course_id: item.order_course_id,
          teacher_id: "",
          // start_date: this.datetime[0],
          // end_date: this.datetime[1]
          // 预收表 - 课消课时 点击不传开始时间和结束时间
          start_date: "",
          end_date: ""
        }
      });
    },

    // 排班成功
    addClassSuccess() {
      this.getList();
    },
    // 打开排班控件
    toAddClass(item) {
      let time = parseInt(item.times - item.used_times);
      this.is_one_to_one = item.is_one_to_one;
      if (time === 0) {
        this.$message.error("剩余课时为0不支持排入班级");
        return;
      }
      this.bindCourseInfo = item;
      this.showClassChoose = true;
    },
    toOrder(item) {
      this.$router.push({
        path: "/recruit_student/order_detail_new",
        query: {
          order_id: item.order_id
        }
      });
    },
    exportList() {
      let obj = {
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        subject: this.subject,
        term: this.term,
        has_class: this.hasClass,
        warning: this.warning
      };
      exportRevenueList(obj)
        .then(res => {
          this.$downLoad(res.data);
          this.$message.success("导出成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error("导出失败");
        });
    },
    filterChange(e, type) {
      if (type !== "page") this.page = 1;
      this[type] = e;
      this.getList();
    },
    getList() {
      let obj = {
        page: this.page,
        size: this.size,
        search: this.search,
        // start_date: this.datetime[0],
        // end_date: this.datetime[1],
        subject: this.subject,
        term: this.term,
        has_class: this.hasClass,
        warning: this.warning
      };
      this.tableLoading = true;
      getRevenueList(obj)
        .then(res => {
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          this.$message.error(e);
          this.tableLoading = false;
        });
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData",
      isNewType: "common/getSystemType"
    })
  },
  components: {
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate,
    "v-choose-class": chooseClass
  }
};
</script>
