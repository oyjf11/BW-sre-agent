<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      ref="tableWrap"
      :defaultExport="true"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      @toExport="toExport"
    >
<!--      筛选模块-->
      <template slot="searchItems">
<!--        原先的筛选栏样式-->
        <!--<v-radio-bar
          label="班级"
          :radioList="searchData.class_status"
          @onChange="filterChange($event,'class_status')"
        ></v-radio-bar>
        <v-mutex-check-bar
          label="学期"
          :checkList="searchData.term"
          @onChange="filterChange($event,'term')"
        ></v-mutex-check-bar>
        <v-time-bar
          :all="false"
          :time="datetime"
          :timeList="timeLabelList"
          :timePickerOption="pickerOptions"
          @onChange="filterChange($event,'datetime')"
        ></v-time-bar>-->

<!--        改版后的筛选栏样式-->
        <v-filter-date
          ref="FilterDate"
          label="筛选时间"
          :transDate="transDate"
          :date-list="timeLabelList"
          @onChange="filterChange($event,'datetime')"
          slot="searchItems"
        ></v-filter-date>
        <v-filter-select
          label="筛选班级"
          :select-list="searchData.class_status"
          @onChange="filterChange($event,'class_status')"
          slot="searchItems"
        ></v-filter-select>
        <v-filter-select
          label="筛选学期"
          :select-list="searchData.term"
          @onChange="filterChange($event,'term')"
          slot="searchItems"
        ></v-filter-select>
      </template>
      <template slot="table_title">家校统计</template>
      <el-button slot="table_btns" @click="exportList(1)">导出列表</el-button>
      <el-button slot="table_btns" @click="exportList(2)">导出分校明细</el-button>
      <template slot="table_count">
        <p v-if="limitTime">更新日期：{{limitTime | formatToDate("Y-M-D h:m")}}</p>
        <p>
          <span>排班学生数:{{studentNum}}</span>
          <span>绑定数:{{bindNum}}</span>
          <span>绑定率:{{bindRate}}</span>
        </p>
        <p>
          <span>教师数:{{teacherNum}}</span>
          <span>绑定数:{{teacherBindNum}}</span>
          <span>绑定率:{{teacherBindRate}}</span>
        </p>
      </template>
      <el-table slot="table" :data="listData" ref="tableList" v-loading="loading" class="pub-table">
        <el-table-column
          v-for="item in headerList"
          :key="item.id"
          v-if="item.show"
          :label-class-name="item.id.toString()"
          :sortable="item.sortable"
          :formatter="tableContentFormate"
          :prop="item.prop"
        >
          <template slot="header" slot-scope="scope">
            <el-tooltip placement="bottom">
              <div slot="content" class="tool_tips_box" v-if="item.tooltip" v-html="item.tooltip"></div>
              <span style="font-weight: 600" v-if="item.tooltip">{{item.text}}<i class="hoo hoo-feedback_fill"></i></span>
            </el-tooltip>
            <span style="font-weight: 600" v-if="!item.tooltip">{{item.text}}</span>
          </template>
          <el-table-column
            v-for="(subItem,index) in item.children"
            :key="index"
            :width="subItem.width"
            v-if="item.children.length !== 0"
            :label-class-name="subItem.id.toString()+ ' '  + subItem.parentProp.toString()"
            :label="subItem.text"
            :sortable="subItem.sortable"
            :formatter="tableContentFormate"
            :prop="subItem.prop"
          ></el-table-column>
        </el-table-column>
        <el-table-column :render-header="tableSetting" fixed="right" min-width="100">
          <template slot-scope="scope">
            <el-button type="text" @click="toDetails(scope.row)">查看老师详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-table-setting :dialog="dialogShow" :index="headerListIndex" @onClose="dialogClose"></v-table-setting>
  </div>
</template>

<script>
import { getGrowthAnalyseIndex } from "@/api/statistical";
import { AttrList } from "@/api/operations_center";
import pubTableSetting from "@/components/pub_table_setting.vue";
import timeBar from "@/components/top_box/time_bar";
import radioBar from "@/components/top_box/radio_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import FilterDateBar from "@/components/top_box/filter_date_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from "vuex";
import { exportFile } from "@/api/exports";
export default {
  data() {
    return {
      exportType: "",
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      pickerOptions: {
        unLink: true,
        options: {
          onPick: ({ maxDate, minDate }) => {
            this.pickDate = maxDate ? null : minDate.getTime();
          },
          disabledDate: time => {
            let nowDate = new Date(new Date().setHours(0, 0, 0, 0));
            let tomorrow = nowDate.setDate(nowDate.getDate() + 1);
            if (time >= tomorrow) {
              return true;
            }
            return false;
          }
        }
      },
      datetime: [],
      transDate: [],
      loading: false,
      listData: [],
      page: 1,
      count: 0,
      size: 10,
      limitTime: null,
      order_by: "",
      bindNum: 0,
      studentNum: 0,
      teacherNum: 0,
      teacherBindNum: 0,
      term: "",
      class_status: "",
      isInit: false,
      dialogShow: false,
      headerList: null,
      headerListIndex: 0,
      orginList: [
        {
          show: true,
          text: "机构名称",
          id: 1,
          prop: "org_name"
        },
        {
          show: true,
          text: "绑定比",
          id: 4,
          prop: "student_bind_rate",
          tooltip: "已在小程序绑定手机号码的学生人数/班级所有学生人数（不包括担任助教的班级）"
        },
        {
          show: true,
          text: "课后点评",
          id: 9,
          prop: "growth_archive_image_text_count",
          tooltip: "总数：</br>老师发布课后点评的数量(针对全部发只算一条)</br></br> 查看比：</br>已查看的学生数量(如绑定多名家长，只要有一位家长看见即为已查看)/发布课后点评的全部学生数量(针对全部发的一条包括 45个学生)</br></br>点赞数：</br>点赞了该条课后点评的家长人数(老师自己也可点赞)</br></br>评论数：</br>该条课后点评所有的评论和回复数量(包括老师自己发布的点评和回复家长的内容)",
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_image_text_count",
              id: "sub-9",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 150,
              parentProp: "growth_archive_image_text_count",
              id: "sub-rate"
            },
            {
              show: true,
              text: "点赞数",
              width: 80,
              parentProp: "growth_archive_image_text_count",
              id: "sub-11",
              prop: "like"
            },
            {
              show: true,
              text: "评论数",
              parentProp: "growth_archive_image_text_count",
              width: 80,
              id: "sub-12",
              prop: "reply"
            }
          ]
        },
        /*{
          show: false,
          text: "学习反馈",
          id: "feedback",
          prop: "growth_archive_study_feedback",
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_study_feedback_count",
              id: "sub-20",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 150,
              parentProp: "growth_archive_study_feedback_count",
              id: "sub-rate"
            },
            {
              show: true,
              text: "点赞数",
              width: 80,
              parentProp: "growth_archive_study_feedback_count",
              id: "sub-21",
              prop: "like"
            },
            {
              show: true,
              text: "评论数",
              parentProp: "growth_archive_study_feedback_count",
              width: 80,
              id: "sub-22",
              prop: "reply"
            }
          ]
        },*/
        {
          show: true,
          text: "学员成绩",
          id: 88,
          prop: "growth_archive_unit_test",
          tooltip: '总数：</br>老师发布学员成绩的数量(针对全部发只算一条)</br></br>查看比：</br>已查看的学生数量(如绑定多名家长，只要有一位家长看见即为已查看)/发布学员成绩的全部学生数量(针对全部发的一条包括 45个学生)',
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_unit_test_count",
              id: "88-count",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 140,
              parentProp: "growth_archive_unit_test_count",
              id: "sub-rate",
              prop: "count"
            }
          ]
        },
        {
          show: true,
          text: "学员作业",
          id: 13,
          prop: "growth_archive_mission_count",
          tooltip: '总数：</br>老师发布学员作业的数量（针对全部发只算一条）</br></br>查看比：</br>已查看的学生数量(如绑定多名家长，只要有一位家长看见即为已查看)/发布学员作业的全部学生数量(针对全部发的一条包括 45个学生)</br></br>完成比：</br>已完成的学生数量/发布学员作业的全部学生数量',
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_mission_count",
              id: "sub-13",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 140,
              parentProp: "growth_archive_mission_count",
              id: "sub-rate",
              prop: "count"
            },
            {
              show: true,
              text: "完成比",
              width: 140,
              parentProp: "growth_archive_mission_count",
              id: "sub-finish",
              prop: "count"
            }
          ]
        },
        {
          show: true,
          text: "班级通知",
          id: 5,
          prop: "growth_archive_class_count",
          tooltip: '总数：</br>老师发布班级通知的数量(针对全部发只算一条)</br></br>查看比：</br>已查看的学生数量(如绑定多名家长，只要有一位家长看见即为已查看)/发布学班级通知的全部学生数量(针对全部发的一条包括 45个学生)',
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_class_count",
              id: "sub-5",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 150,
              parentProp: "growth_archive_class_count",
              id: "sub-rate"
            }
            // {
            //   show: true,
            //   text: "点赞数",
            //   width: 80,
            //   parentProp: "growth_archive_class_count",
            //   id: "sub-7",
            //   prop: "like"
            // },
            // {
            //   show: true,
            //   text: "评论数",
            //   parentProp: "growth_archive_class_count",
            //   width: 80,
            //   id: "sub-8",
            //   prop: "reply"
            // }
          ]
        }
      ],
      searchForm: { // 搜索条件
        search: '',
        start_date: '',
        end_date: '',
        source_id: 0,
        status: 0,
        show_standstill_only: 0
      },
    };
  },
  created() {
    /*let endDate = new Date().setHours(23, 59, 59, 0);
    let startDate = new Date().setHours(0, 0, 0, 0);
    startDate = startDate - 6 * 24 * 60 * 60 * 1000;
    this.datetime = [startDate / 1000, endDate / 1000];*/
    this.init();
    this.setTableHeader();
  },
  methods: {
    /**
     * 获取当前时间与上一个月的时间，默认显示最近一个月的数据
     */
    init() {
      let dateArr = [];
      let myDate = new Date();
      myDate.setDate(myDate.getDate() - 30);
      let dateTemp;  // 临时日期数据
      let flag = 1;
      for (let i = 0; i < 31; i++) {
        dateTemp = myDate.getFullYear() + '-' +(myDate.getMonth()+1)+"-"+myDate.getDate();
        dateArr.push(dateTemp);
        myDate.setDate(myDate.getDate() + flag);
      }
      this.transDate = [dateArr[0], dateArr[dateArr.length - 1]];
      let s = new Date(dateArr[0]);
      let e = new Date(dateArr[dateArr.length-1]);
      this.datetime = [s.getTime() / 1000, e.getTime() / 1000 + 86399];
    },
    toExport() {
      let obj = {
        term: this.term,
        class_status: this.class_status,
        order_by: this.order_by,
        start_time: this.datetime[0],
        end_time: this.datetime[1],
        org_id: localStorage.getItem("org_id"),
        user_id: localStorage.getItem("user_id")
      };
      exportFile({
        type: this.exportType / 1 === 1 ? "growth.teacher_detail" : "growth.org_detail",
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
    exportList(type) {
      this.exportType = type;
      this.$refs.tableWrap.openExport();
    },
    setTableHeader() {
      this.$store
        .dispatch("table/checkHeaderList", {
          originList: this.orginList,
          index: this.headerListIndex
        })
        .then(res => {
          this.headerList = res;
        })
        .catch(res => {
          this.headerList = this.orginList;
        });
    },
    tableContentFormate(row, column, cellValue, index) {
      let labelClassName = column.labelClassName;
      let prop = column.property;
      let arr = labelClassName.split(" ");
      //arr[1] parentProp
      if (arr[1]) {
        if (labelClassName.indexOf("rate") >= 0) {
          let rate = 0;
          let count = row[arr[1]].read_count + row[arr[1]].unread_count;
          if (count !== 0) rate = ((row[arr[1]].read_count / count) * 100).toFixed(2);
          return `${rate}% (${row[arr[1]].read_count} / ${count})`;
        } else if (labelClassName.indexOf("finish") >= 0) {
          let rate = 0;
          let count = row[arr[1]].finish_count + row[arr[1]].unfinish_count;
          if (count !== 0) rate = ((row[arr[1]].finish_count / count) * 100).toFixed(2);
          return `${rate}% (${row[arr[1]].finish_count} / ${count})`;
        } else {
          return row[arr[1]][prop];
        }
      }
      return cellValue;
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      console.log('%cdataTime','font-size:40px;color:pink',this.datetime)
      this.loading = true;
      let obj = {
        org_name: this.$store.getters.org_name,
        page: this.page,
        count: this.size,
        term: this.term,
        class_status: this.class_status,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      };
      getGrowthAnalyseIndex(obj)
        .then(res => {
          this.loading = false;
          this.count = res.data.count / 1;
          if (res.data.show_feedback / 1 === 1) {
            for (let i = 0; i < this.orginList.length; i++) {
              if (this.orginList[i].id === "feedback") {
                this.orginList[i].show = true;
                break;
              }
            }
            this.setTableHeader();
          }
          let list = res.data.list;
          let keys = Object.keys(list);
          this.listData = Array.from({ length: keys.length }).map((val, index) => {
            let temp = this.$copyObject(list[keys[index]]);
            temp.org_id = keys[index];
            return temp;
          });
          this.bindNum = res.data.student_bind_number;
          this.studentNum = res.data.student_number;
          this.teacherBindNum = res.data.teacher_bind_number;
          this.teacherNum = res.data.teacher_number;
        })
        .catch(e => {
          this.loading = false;
        });
    },
    toDetails(item) {
      this.$router.push({
        name: "miniProgram_teacher_list",
        query: { org_id: item.org_id, start_time: this.datetime[0], end_time: this.datetime[1] }
      });
    },
    tableSetting(h, { column, $index }) {
      let RetrunData = h(
        "span",
        {
          class: {
            "table-setting-icon": true
          }
        },
        [
          h("span", {}, "操作"),
          h("i", {
            class: {
              hoo: true,
              "hoo-xitongshezhi": true
            },
            on: { click: this.handleTableSetting }
          })
        ]
      );
      return RetrunData;
    },
    handleTableSetting() {
      this.dialogShow = true;
    },
    dialogClose(refresh) {
      this.dialogShow = false;
      if (refresh) {
        this.headerList = JSON.parse(this.$store.getters.headerList)[this.headerListIndex];
        this.$refs.tableList.doLayout();
      }
    }
  },
  computed: {
    bindRate() {
      if (this.studentNum == 0) {
        return "0%";
      } else {
        return ((this.bindNum / this.studentNum) * 100).toFixed(2) + "%";
      }
    },
    teacherBindRate() {
      if (this.teacherNum == 0) {
        return "0%";
      } else {
        return ((this.teacherBindNum / this.teacherNum) * 100).toFixed(2) + "%";
      }
    },
    ...mapGetters({ searchData: "common/getSearchData" })
  },
  components: {
    "v-table-setting": pubTableSetting,
    "v-time-bar": timeBar,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-filter-select": FilterSelectBar,
    "v-filter-date": FilterDateBar,
    "v-table-wrap": tableTemplate
  },
  activated() {
    this.getList();
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
  .cell sub-finish growth_archive_mission_count
    font-weight 400!important
  .tool_tips_box {
    font-size 14px
    line-height 20px
    font-weight 600
    width 312px
  }
  .hoo-feedback_fill
    color #8690ac
</style>
