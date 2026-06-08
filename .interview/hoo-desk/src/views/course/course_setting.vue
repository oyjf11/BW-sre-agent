<template>
  <v-table-wrap
    :page='page'
    :total="count"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <!-- showSearch
    placeholder="请输入课程名称"
    @onSearch="filterChange($event,'search')" -->
    <el-button slot="buttons" type="primary" @click="creatCourse">新建课程</el-button>
    <v-search-new-bar
      label="课程名称"
      placeholder="请输入课程名称"
      @onSearch="filterChange($event,'search')"
      slot="searchItems"
    ></v-search-new-bar>
      <!-- @onSearch="handleSearch" -->
    <v-filter-select-bar
      label="筛选科目"
      :select-list="commonSearchList.subject"
      @onChange="filterChange($event,'subject')"
      slot="searchItems"
    ></v-filter-select-bar>
    <v-filter-select-bar
      label="筛选学期"
      :select-list="commonSearchList.term"
      @onChange="filterChange($event,'term')"
      slot="searchItems"
    ></v-filter-select-bar>
    <v-filter-select-bar
      label="课程类型"
      :is_trans_id=true
      attr="label"
      :select-list="class_type"
      @onChange="filterChange($event,'is_one_to_one')"
      slot="searchItems"
    ></v-filter-select-bar>
    <v-filter-select-bar
      label="筛选年级"
      :select-list="commonSearchList.grade"
      @onChange="filterChange($event,'grade')"
      slot="searchItems"
    ></v-filter-select-bar>
      <!-- :select-list="channalList"
      @onChange="channalChange" -->
    <!-- <template slot="searchItems">
      <v-radio-bar label="类别" :radioList="typeList" @onChange="filterChange($event,'attend_type')"></v-radio-bar>
    </template> -->
    <template slot="table_title">模板列表</template>
    <div class="count" slot="table_count">
      当前结果：共计
      <i style="color:#f86b6e;">{{count}}</i>个课程
    </div>

    <el-table
      slot="table"
      ref="multipleTable"
      :data="listData"
      tooltip-effect="dark"
      class="pub-table"
      v-loading="tableLoading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column label="类别">
        <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
      </el-table-column>
      <el-table-column prop="course_name" label="课程名称"></el-table-column>
      <el-table-column prop="subject_name" label="科目"></el-table-column>
      <el-table-column prop="course_term" label="学期" show-overflow-tooltip></el-table-column>
      <el-table-column prop="start_date" label="开始时间" show-overflow-tooltip>
        <template slot-scope="scope">
          <template
            v-if="scope.row.start_date && scope.row.start_date !=0"
          >{{scope.row.start_date | formatToDate("Y-M-D")}}</template>
          <template v-else>未设置时间</template>
        </template>
      </el-table-column>
      <el-table-column prop="sub_total" label="学费总计" show-overflow-tooltip>
        <template slot-scope="scope">{{scope.row.sub_total}}</template>
      </el-table-column>
      <el-table-column prop="is_open" label="课程状态" show-overflow-tooltip>
        <template slot-scope="scope">
          <!-- <el-switch v-model="scope.row.is_open" @change="openStatusChange($event,scope.row)"></el-switch> -->
          {{scope.row.is_open / 1===1 ? "上架":"下架"}}
        </template>
      </el-table-column>
      <el-table-column label="操作" class-name="table-btn-column" width="180">
        <template slot-scope="scope">
          <el-button type="text" @click="handleClick(scope.row)">编辑</el-button>
          <el-button type="text" @click="handleCancel(scope.row)">删除</el-button>
          <el-button type="text" @click="handleCopy(scope.row)">复制</el-button>
        </template>
      </el-table-column>
    </el-table>
  </v-table-wrap>
</template>

<script>
import {
  getCourseList,
  deliverList,
  deleteCourse,
  updataCourse,
  creatCourse,
  getCommonSearchParam
} from "@/api/course_control";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
import searchNewBar from "@/components/top_box/search_new_bar";
import filterSelectBar from "@/components/top_box/filter_select_bar";
import {mapGetters } from "vuex";
export default {
  data() {
    return {
      search: "",
      datetime: "",
      checkList: "",
      count: 0,
      page: 1,
      size: 10,
      attend_type: "",
      subject: "",
      grade: "",
      term: "",
      is_one_to_one: "",
      listData: [],
      multipleSelection: [],
      order_list: [],
      tableLoading: false,
      typeLabel: this.$store.getters.getAttendTypeLabel,
      typeList: this.$store.getters.getAttendType,
      commonSearchList: [],
      class_type: [
        {attr_id: 1, attr_value: '班课', label: '班课'},
        {attr_id: 2, attr_value: '一对一', label: '一对一'},
      ]
    };
  },
  activated() {
    // 新版不请求
    if(!this.isNewType) this.getList();

    // 首页操作指引 点击进入获取列表数据
    if(this.$route.params.status == 1) this.getList();
    this.getCommonSearchList();
  },
  components: {
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate,
    "v-search-new-bar": searchNewBar,
    "v-filter-select-bar": filterSelectBar,
  },
  methods: {
    getCommonSearchList() {
      getCommonSearchParam()
        .then(res => {
          this.commonSearchList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    filterChange(val, type) {
      let value = 0;
      if (type !== "page") this.page = 1;
      if (type == 'is_one_to_one') {
        if (val == 0) {
          value = ''
        } else {
          value = Number(val) - 1;
        }
      } else {
        value = val
      }
      this[type] = value;
      this.getList();
    },
    openStatusChange($event, row) {
      let data = row;
      let obj = {
        course_id: data.course_id,
        is_open: $event ? 1 : 0
      };
      updataCourse(obj)
        .then(res => {
          this.$message.success("修改成功");
        })
        .catch(e => {
          data.is_open = !$event;
          this.$message.error("修改失败");
        });
    },
    // 获取课程列表
    getList(data) {
      this.tableLoading = true;
      getCourseList({
        page: this.page,
        search: this.search,
        size: this.size,
        // attend_type: this.attend_type,
        subject: this.subject,
        grade: this.grade,
        term: this.term,
        is_one_to_one: this.is_one_to_one,
      })
        .then(res => {
          let listData = res.data.list;
          listData.forEach(i => {
            i.is_open = i.is_open / 1 === 1;
          });
          this.listData = listData;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(error => {
          console.log("error", error);
          this.tableLoading = false;
          this.$message.error(error);
        });
    },
    // 新建课程
    creatCourse() {
      this.$router.push({
        path: "/course/creat_course",
        query: {}
      });
    },
    // 课程编辑
    handleClick(data) {
      this.$router.push({
        path: "/course/creat_course",
        query: {
          course_id: data.course_id
        }
      });
    },
    handleCopy(data) {
      let obj = {
        course_name: data.course_name + "-副本",
        course_term: data.course_term,
        subject_name: data.subject_name,
        grade: data.grade,
        sundry_fees: data.sundry_fees,
        reduce: data.reduce,
        discount: data.discount,
        is_open: data.is_open ? "1" : "0",
        remark: data.remark,
        use_org: data.use_org,
        start_date: data.start_date,
        end_date: data.end_date,
        price: data.price,
        hours: data.hours,
        times: data.times,
        is_one_to_one: data.is_one_to_one,
        attend_type: data.attend_type,
        time_table: JSON.stringify(data.time_table),
        use_org: JSON.stringify(data.use_org)
      };
      creatCourse(obj)
        .then(res => {
          console.log(res, "新建副本返回");
          this.$message.success("新增副本成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error("新增副本失败");
        });
    },
    handleCancel(rows) {
      let course_id = rows.course_id;
      this.$confirm("此操作将永久撤销课程, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          deleteCourse(course_id)
            .then(res => {
              this.$message.success("删除课程成功");
              this.getList();
            })
            .catch(error => {
              this.$message.error(error);
            });
        })
        .catch(() => {});
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
    }
  },
  computed:{
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
  },
};
</script>


<style scoped lang="stylus" rel="stylesheet/stylus">
</style>
