<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <v-time-bar
        slot="searchItems"
        :all="false"
        :time="datetime"
        :timeList="timeLabelList"
        :timePickerOption="timePickerOption"
        @onChange="filterChange($event,'datetime')"
      ></v-time-bar>
      <template slot="table_title">教师排行榜</template>
      <el-table
        slot="table"
        :data="listData"
        @sort-change="sortChange"
        v-loading="listLoading"
        class="pub-table"
      >
        <el-table-column type="index"></el-table-column>
        <el-table-column
          v-for="item in headerList"
          :key="item.id"
          v-if="item.show"
          :label-class-name="item.id.toString()"
          :label="item.text"
          :sortable="item.sortable"
          :prop="item.prop"
        ></el-table-column>
        <el-table-column :render-header="tableSetting" min-width="100"></el-table-column>
      </el-table>
    </v-table-wrap>
    <v-table-setting :dialog="dialogShow" :index="headerListIndex" @onClose="dialogClose"></v-table-setting>
  </div>
</template>



<script>
import { getTeacherPartList } from "@/api/statistical";
import pubTableSetting from "@/components/pub_table_setting.vue";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      timeLabelList: [7, 30].map(i => ({ value: i, label: i + "天" })),
      timePickerOption: {
        options: {
          disabledDate(time) {
            return time.getTime() > Date.now();
          }
        }
      },
      datetime: [],
      page: 1,
      size: 10,
      count: 0,
      listData: [],
      order_by: "",
      listLoading: false,
      dialogShow: false,
      orginList: [
        { show: true, text: "校区", id: 1, prop: "org_name" },
        { show: true, text: "教师", id: 2, prop: "teacher_name" },
        {
          show: true,
          text: "档案数",
          id: 3,
          prop: "comment_number_total",
          sortable: "custom"
        },
        {
          show: true,
          text: "点赞数",
          id: 4,
          prop: "like_number_total",
          sortable: "custom"
        },
        {
          show: true,
          text: "评论数",
          id: 5,
          prop: "student_comment_number_total",
          sortable: "custom"
        },
        {
          show: true,
          text: "小任务数",
          id: 6,
          prop: "mini_task_number_total",
          sortable: "custom"
        }
      ],
      headerList: [],
      headerListIndex: 2,
      timeOptions: {
        disabledDate(time) {
          return time.getTime() > Date.now();
        }
      }
    };
  },
  components: {
    "v-table-setting": pubTableSetting,
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate
  },
  created() {
    let endDate = new Date().setHours(23, 59, 59, 0);
    let startDate = new Date().setHours(0, 0, 0, 0);
    startDate = startDate - 6 * 24 * 60 * 60 * 1000;
    this.datetime = [startDate / 1000, endDate / 1000];
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
  activated(){
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    sortChange(data) {
      switch (data.prop) {
        case "comment_number_total":
          this.order_by =
            data.order == "ascending" ? "comment_number_asc " : "comment_number_desc ";
          break;
        case "like_number_total":
          this.order_by = data.order == "ascending" ? "like_number_asc" : "like_number_desc";
          break;
        case "student_comment_number_total":
          this.order_by =
            data.order == "ascending"
              ? "student_comment_number_asc"
              : "student_comment_number_desc";
          break;
        case "mini_task_number_total":
          this.order_by =
            data.order == "ascending" ? "mini_task_number_asc" : "mini_task_number_desc";
          break;
        default:
          this.order_by = "";
      }
      this.page = 1;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getTeacherPartList({
        page: this.page,
        count: this.size,
        order_by: this.order_by,
        start_time: this.datetime[0],
        end_time: this.datetime[1]
      })
        .then(res => {
          console.log(res);
          this.listData = res.data.list;
          this.count = res.data.total / 1;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("获取数据失败");
          this.listLoading = false;
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
          // h("span", {}, "操作"),
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
      }
    }
  },
  computed:{
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
  },
};
</script>
