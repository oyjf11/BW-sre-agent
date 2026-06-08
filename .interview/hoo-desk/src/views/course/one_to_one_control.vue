<template>
  <div class="index-wrap">
    <v-table-wrap
      :page="page"
      :total="count"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="creatclass">新建班级</el-button>
      <el-button slot="buttons"  @click="toClassCalendar">课程表</el-button>
      <template slot="searchItems">
        <v-radio-bar
          label="状态"
          @onChange="filterChange($event,'class_status')"
          :radioList="searchData.class_status"
        ></v-radio-bar>
        <v-radio-bar
          label="科目"
          @onChange="filterChange($event,'subject')"
          :radioList="searchData.subject"
        ></v-radio-bar>
        <v-radio-bar
          label="学期"
          @onChange="filterChange($event,'term')"
          :radioList="searchData.term"
        ></v-radio-bar>
        <v-search-bar placeholder="请输入班级或教师或学员名称" @onSearch="filterChange($event,'search')"></v-search-bar>
      </template>
      <template slot="table_title">班级信息</template>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{count}}</i>个课程
      </div>
      <el-table
        ref="multipleTable"
        :data="class_list"
        tooltip-effect="dark"
        class="pub-table"
        v-loading="tableLoading"
        slot="table"
      >
        <el-table-column label="学生姓名">
          <template slot-scope="scope">{{scope.row.student_names}}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级名称"></el-table-column>
        <el-table-column label="收费类型">
          <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="教师"></el-table-column>
        
        <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="160">
          <template slot-scope="scope">
            <el-button type="text" @click="handleDetail(scope.row)">查看详情</el-button>
            <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
            <!-- v-show="scope.row.student_names === '' " -->
            <el-button
              type="text"
              
              @click="handleDel(scope.row)"
            >删除</el-button>
            <!-- <el-button type="text"  @click="handleStudent(scope.row)">学员排班</el-button>
            <el-button type="text" class="no-line" @click="handleCopy(scope.row)">创建副本</el-button> -->
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-stu-control
      :dialog="dialogShow"
      :id="dialogBindId"
      @onClose="stuControlClose"
      @refresh="toRefresh"
    ></v-stu-control>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import searchBar from "@/components/top_box/search_bar";
import { ClassList, creatClass, searchParam, deleteClass, classInfo } from "@/api/class_control";
import classStudentControl from "./class_student_control";
import oneToOneControl from "./one_to_one_control";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      search: "",
      datetime: "",
      checkList: "",
      count: 0,
      page: 1,
      page_count: 10,
      attend_type: "",
      class_list: [],
      multipleSelection: [],
      subject_list: [],
      term_list: [],
      class_status_list: [],
      subject: "",
      term: "",
      class_status: "0",
      dialogShow: false,
      dialogBindId: "",
      tableLoading: false,
      typeLabel: this.$store.getters.getAttendTypeLabel,
      typeList: this.$store.getters.getAttendType,
      activeName: 'class'
    };
  },
  activated() {
    this.getClassListOneToOne();
  },
  components: {
    "v-stu-control": classStudentControl,
    "v-one-to-one-control": oneToOneControl,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    handleClick(tab, event) {
      console.log(tab, event);
    },
    toClassCalendar(){
      this.$router.push({path:"/course/class_calendar"})
    },
    filterChange(e, type) {
      if (type !== "page") this.page = 1;
      this[type] = e;
      this.getClassListOneToOne();
    },
    getClassListOneToOne() {
      let obj = {
        page: this.page,
        search: this.search,
        size: this.page_count,
        term: this.term,
        attend_type: this.attend_type,
        subject: this.subject,
        class_status: this.class_status,
        is_one_to_one: 1 // 0: 班课; 1: 一对一;
      };
      this.tableLoading = true;
      ClassList(obj)
        .then(res => {
          console.log("res", res.data);
          this.class_list = res.data.list;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(error => {
          this.tableLoading = false;
          this.$message.error(error);
        });
    },
    handleEdit(item) {
      this.$router.push({
        name: "creat_class",
        query: {
          class_id: item.class_id,
          is_one_to_one: '1'
        }
      });
    },
    handleDetail(item) {
      console.log('%cnowList','font-size:40px;color:pink;',item)
      this.$router.push({
        name: "class_detail",
        query: {
          class_id: item.class_id,
          is_endTime: item.end_time,
          is_one_to_one: item.is_one_to_one,
          nowList: item
        }
      });
    },
    handleDel(item) {
      this.$confirm("此操作将永久删除该班级, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteClass(item.class_id);
        })
        .then(res => {
          if (res) {
            console.log("删除成功", res);
            this.$message.success("删除成功");
            this.getClassListOneToOne();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    //创建副本
    handleCopy(item) {
      classInfo({ class_id: item.class_id })
        .then(res => {
          console.log(res, "详情返回");
          let info = res.data;
          info.class_name = info.class_name + "-副本";
          // info.student_list = JSON.stringify(info.student_list);
          info.student_list = JSON.stringify([]);
          info.time_table = JSON.stringify(info.time_table);
          info.week_list = JSON.stringify(info.week_list);
          delete info.class_id;
          return creatClass(info);
        })
        .then(res => {
          console.log("新增返回", res);
          this.$message.success("新增成功");
          this.getClassListOneToOne();
        })
        .catch(e => {
          console.log(e);
          this.$message.error("新建副本失败");
        });
    },
    //编辑学生
    handleStudent(item) {
      this.dialogShow = true;
      this.dialogBindId = item.class_id;
    },
    stuControlClose() {
      this.dialogShow = false;
    },
    toRefresh() {
      this.getClassListOneToOne();
    },
    creatclass() {
      this.$router.push({
        name: "creat_class",
        query: {
          is_one_to_one: '1'
        }
      });
    },
    pageChange(val) {
      this.page = val;
      this.getClassListOneToOne();
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData"
    })
  },
  filters: {
    stuFormate(val) {
      if (val) {
        return val.replace(/,/g, "、");
      }
    }
  }
};
</script>

<style lang="stylus" scoped>
.pub-filter-box
  .filter-item
    .el-radio
      margin-left: 0;
      margin-right: 10px;
      margin-bottom: 10px;
.stu-text
  max-height: 44px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  -moz-line-clamp: 2;
  display: -moz-box;
  -moz-box-orient: vertical;
.stu-list
  .el-button
    margin-bottom: 10px;
</style>
