<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      ref="tableWrap"
      :defaultBtn="true"
      :defaultExport="true"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      @toExport="toExport"
    >
      <template slot="searchItems">
        <!-- <v-radio-bar
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
        ></v-time-bar> -->
        <v-filter-date
          :transDate="transDate"
          ref="FilterDate"
          label="筛选时间"
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
      <el-table
        slot="table"
        :data="listData"
        ref="tableList"
        v-loading="loading"
        @sort-change="sortChange"
        class="pub-table"
      >
        <el-table-column
          v-for="(item,i) in headerList"
          :key="i"
          v-if="item.show"
          :label-class-name="item.id.toString()"
          :label="item.text"
          :sortable="item.sortable"
          :formatter="tableContentFormate"
          :prop="item.prop"
          :width="item.width"
        >
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
            <el-button type="text" @click="toDetails(scope.row)">查看内容详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-bind-list
      :isShow="bindShow"
      :id="bindId"
      :orgId="org_id"
      :filter="bindFilter"
      @onClose="bindClose"
    ></v-bind-list>
    <v-table-setting :dialog="dialogShow" :index="headerListIndex" @onClose="dialogClose"></v-table-setting>
  </div>
</template>

<script>
import { getTeacherList } from "@/api/statistical";
import { AttrList } from "@/api/operations_center";
import pubTableSetting from "@/components/pub_table_setting.vue";
import listDialog from "./bind_list";
import timeBar from "@/components/top_box/time_bar";
import radioBar from "@/components/top_box/radio_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from "vuex";
import { exportFile } from "@/api/exports";
import filterSelectBar from "@/components/top_box/filter_select_bar";
import filterDateBar from "@/components/top_box/filter_date_bar";
export default {
  data() {
    return {
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
      transDate: [],
      termList: [],
      org_id: 0,
      loading: false,
      listData: [],
      order_by: "",
      limitTime: null,
      bindNum: 0,
      studentNum: 0,
      page: 1,
      size: 10,
      count: 0,
      teacherNum: 0,
      teacherBindNum: 0,
      term: "",
      class_status: "",
      classStatusList: [
        { value: "未上课", label: "未上课" },
        { value: "在上课", label: "在上课" },
        { value: "已结班", label: "已结班" }
      ],
      datetime: [],
      bindShow: false,
      bindId: null,
      bindFilter: {
        class_status: "",
        term: []
      },
      headerList: null,
      headerListIndex: 1,
      orginList: [
        { show: true, text: "科目", id: 99, prop: "subject_name" },
        { show: true, text: "教师名称", id: 1, prop: "teacher_name" },
        { show: true, text: "是否绑定", id: "isBind", prop: "is_bind" },
        { show: true, text: "班级绑定比", id: "classBindRate", prop: "" },
        {
          show: true,
          text: "绑定率",
          id: "bindRate",
          prop: "bind_rate",
          sortable: "custom",
          width: 88
        },
        {
          show: true,
          text: "课后点评",
          id: 9,
          prop: "growth_archive_image_text_total",
          children: [
            {
              show: true,
              text: "总数",
              width: 80,
              parentProp: "growth_archive_image_text_total",
              id: "sub-9",
              prop: "count"
            },
            {
              show: true,
              text: "查看比",
              width: 150,
              parentProp: "growth_archive_image_text_total",
              id: "sub-rate",
              sortable: "custom"
            },
            {
              show: true,
              text: "点赞数",
              width: 88,
              parentProp: "growth_archive_image_text_total",
              id: "like_number",
              prop: "like",
              sortable: "custom"
            },
            {
              show: true,
              text: "评论数",
              parentProp: "growth_archive_image_text_total",
              width: 88,
              id: "student_comment_number",
              prop: "reply",
              sortable: "custom"
            }
          ]
        },
        {
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
        },
        {
          show: true,
          text: "学员成绩",
          id: 88,
          prop: "growth_archive_unit_test_count",
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
      dialogShow: false
    };
  },
  created() {
    let {org_id,start_time,end_time} = this.$route.query;
    this.org_id = org_id;
    if(start_time && end_time){
      this.datetime = [start_time,end_time];
      let a = this.timestampToTime(start_time);
      let b = this.timestampToTime(end_time);
      this.transDate = [a , b];
    }else{
      let endDate = new Date().setHours(23, 59, 59, 0);
      let startDate = new Date().setHours(0, 0, 0, 0);
      startDate = startDate - 6 * 24 * 60 * 60 * 1000;
      this.datetime = [startDate / 1000, endDate / 1000];
    }
    this.getList();
    this.setTableHeader();
  },
  components: {
    "v-bind-list": listDialog,
    "v-table-setting": pubTableSetting,
    "v-time-bar": timeBar,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate,
    "v-filter-select": filterSelectBar,
    "v-filter-date": filterDateBar,
  },
  methods: {
    timestampToTime(str) {
      const date = new Date(str * 1000);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
      var Y = date.getFullYear() + '-';
      var M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
      var D = date.getDate() + ' ';
      var h = date.getHours() + ':';
      var m = date.getMinutes() + ':';
      var s = date.getSeconds();
      return Y + M + D;
    },
    toExport() {
      let obj = {
        org_id: this.$route.query.org_id,
        term: this.term,
        class_status: this.class_status,
        order_by: this.order_by,
        start_time: this.datetime[0],
        end_time: this.datetime[1],
        user_id: localStorage.getItem("user_id")
      };
      exportFile({
        type: "growth.teacher_detail",
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
    setTableHeader() {
      this.$store
        .dispatch("table/checkHeaderList", {
          originList: this.orginList,
          index: this.headerListIndex
        })
        .then(res => {
          this.headerList = res;
        })
        .catch(e => {
          this.headerList = this.orginList;
        });
    },
    bindClose() {
      this.bindShow = false;
    },
    tableContentFormate(row, column, cellValue, index) {
      let labelClassName = column.labelClassName;
      let prop = column.property;
      let arr = labelClassName.split(" ");
      //arr[1] parentProp
      if (arr[1]) {
        let item = row[arr[1]];
        if (labelClassName.indexOf("rate") >= 0) {
          let rate = 0;
          let count = item.send_count / 1;
          if (count !== 0) rate = ((item.read_count / count) * 100).toFixed(2);
          return `${rate}% (${item.read_count} / ${count})`;
        } else if (labelClassName.indexOf("finish") >= 0) {
          let rate = 0;
          let count = item.send_count / 1;
          if (count !== 0) rate = ((item.finish_count / count) * 100).toFixed(2);
          return `${rate}% (${item.finish_count} / ${count})`;
        } else {
          return item[prop];
        }
      }
      switch (labelClassName) {
        case "isBind":
          return row.is_bind ? "是" : "否";
        case "bindRate":
          let a = this.$createElement(
            "span",
            {
              class: "can-click",
              on: { click: this.openBindList.bind(this, row) }
            },
            cellValue
          );
          return a;
          break;
        case "classBindRate":
          return `${row.bind_number} / ${row.student_number}`;
        default:
          return cellValue;
      }
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
    },
    openBindList(item) {
      this.bindShow = true;
      this.bindId = item.teacher_id;
      this.bindFilter = {
        class_status: this.class_status,
        term: this.term
      };
    },
    sortChange(data) {
      console.log("data", data);
      let parseText;
      if (data.column) {
        data = data.column;
        let labelClassName = data.labelClassName;
        let prop = data.property;
        let arr = labelClassName.split(" ");
        parseText = arr[0];
      }
      const tempMap = new Map([
        ["sub-rate", ["read_number_asc", "read_number_desc"]],
        ["like_number", ["like_number_asc", "like_number_desc"]],
        ["student_comment_number", ["comment_number_asc", "comment_number_desc"]],
        ["bindRate", ["bind_rate_asc", "bind_rate_desc"]],
        ["default", ["", ""]]
      ]);
      let item = tempMap.get(parseText) || tempMap.get("default");
      this.order_by = item[data.order === "ascending" ? 0 : 1];
      this.page = 1;
      this.getList();
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.loading = true;
      let obj = {
        org_id: this.$route.query.org_id,
        page: this.page,
        count: this.size,
        term: this.term,
        class_status: this.class_status,
        order_by: this.order_by,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      };
      getTeacherList(obj)
        .then(res => {
          // console.log("res", res);
          this.loading = false;
          if (res.data.show_feedback / 1 === 1) {
            for (let i = 0; i < this.orginList.length; i++) {
              if (this.orginList[i].id === "feedback") {
                this.orginList[i].show = true;
                break;
              }
            }
            this.setTableHeader();
          }
          this.bindNum = res.data.bind_number;
          this.studentNum = res.data.student_number;
          this.teacherNum = res.data.teacher_number;
          this.teacherBindNum = res.data.teacher_bind_number;
          this.count = Number(res.data.total);
          this.limitTime = res.data.update_time;
          this.listData = this.$copyObject(res.data.returnArray);
        })
        .catch(e => {
          this.loading = false;
          console.log(e);
        });
    },
    toDetails(item) {
      this.$router.push({
        name: "miniProgram_teacher_details",
        query: { org_id: item.org_id, teacher_id: item.teacher_id, start_time: this.datetime[0], end_time: this.datetime[1]}
      });
    }
  },
  computed: {
    ...mapGetters({ searchData: "common/getSearchData" }),
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
    }
  }
};
</script>

