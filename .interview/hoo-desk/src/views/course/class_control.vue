<template>
  <div class="container-wrap">
    <el-tabs v-model="activeName" @tab-click="handleClick">
      <el-tab-pane label="班课" name="classs">
        <v-table-wrap
          :page="page"
          :total="count"
          @pageChange="filterChange($event,'page')"
          @sizeChange="filterChange($event,'size')"
        >
          <el-button slot="buttons" type="primary" @click="creatclass">新建班级</el-button>
          <el-button slot="buttons"  @click="toClassCalendar">课程表</el-button>
          <template slot="searchItems">
            <div class="m-top20"></div>
            <v-search-bar placeholder="请输入班级、学员或教师名称" label="" @onSearch="filterChange($event,'search')"></v-search-bar>
            <div class="m-top20"></div>
            <v-filter-select
              label="筛选科目"
              :select-list="searchData.subject"
              @onChange="filterChange($event,'subject')"
              slot="searchItems"
            ></v-filter-select>
            <v-filter-select
              label="筛选学期"
              :select-list="searchData.term"
              @onChange="filterChange($event,'term')"
              slot="searchItems"
            ></v-filter-select>
            <v-filter-select
              label="筛选状态"
              :select-list="searchData.class_status"
              @onChange="filterChange($event,'class_status')"
              slot="searchItems"
            ></v-filter-select>
          </template>
          <template slot="table_title">班级信息</template>
          <el-button @click="stopClass" slot="table_btns">手动结课</el-button>
          <div slot="table_count">
            当前结果：共计
            <i style="color:#f86b6e;">{{count}}</i>个班级
          </div>
          <el-table
            ref="multipleTable"
            :data="class_list"
            tooltip-effect="dark"
            class="pub-table"
            v-loading="tableLoading"
            slot="table"
            @selection-change="selectionChange"
          >
            <el-table-column type="selection" width="55" fixed="left"></el-table-column>
            <el-table-column label="类别">
              <template slot-scope="scope">
                <el-tooltip placement="right" v-if="scope.row.attend_type == 9">
                  <div slot="content">由老师在小程序上自行创建的班级，老师直接从微信上 <br> 邀请学员加入班级，不需要进行学员分班、排课和考勤</div>
                  <span class="stu-text">{{typeLabel[scope.row.attend_type]}}<i class="hoo hoo-feedback_fill"></i></span>
                </el-tooltip>
                <span class="stu-text" v-if="scope.row.attend_type != 9">{{typeLabel[scope.row.attend_type]}}</span>
              </template>
            </el-table-column>
            <el-table-column prop="class_name" label="班级名称"></el-table-column>
            <el-table-column prop="teacher_name" label="教师"></el-table-column>
            <el-table-column label="状态">
              <template slot-scope="scope">
                <el-tag class="c-pointer"
                  :type="scope.row | formatStatus('tag')"
                  slot="reference"
                >{{scope.row | formatStatus}}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recruit_status" label="已招/计招" width="100">
              <template slot-scope="scope">
                <span>{{scope.row.student_count}}/{{scope.row.class_number}}</span>
              </template>
            </el-table-column>
            <el-table-column label="学员" width="650">
              <template slot-scope="scope">
                <el-tooltip placement="top" popper-class="stu-content">
                  <div slot="content">{{scope.row.student_names | stuFormate}}</div>
                  <span class="stu-text">{{scope.row.student_names | stuFormate}}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="160">
              <template slot-scope="scope">
                <el-button type="text" v-if="scope.row.attend_type != 9" @click="handleDetail(scope.row)">查看详情</el-button>
                <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button type="text" v-show="scope.row.student_names == ''" @click="handleDel(scope.row)">删除</el-button>
                <el-button v-if="scope.row.attend_type != 9" type="text"  @click="handleStudent(scope.row)">学员排班</el-button>
                <el-button v-if="scope.row.attend_type != 9" type="text" class="no-line" @click="handleCopy(scope.row)">创建副本</el-button>
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
      </el-tab-pane>
      <el-tab-pane label="一对一" name="oneToOne">
        <v-one-to-one-control></v-one-to-one-control>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import searchBar from "@/components/top_box/search_new_bar";
import { ClassList, creatClass, searchParam, deleteClass, classInfo, closeClass} from "@/api/class_control";
import classStudentControl from "./class_student_control";
import oneToOneControl from "./one_to_one_control";
import radioBar from "@/components/top_box/radio_bar";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
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
      activeName: 'classs',
      stopClassIds:[]
    };
  },
  activated() {
    this.getClassList();
    console.log(this.typeLabel)
  },
  // created() {
  //   for (let i = 0; i < 5; i++) {
  //     this.courseTempList.get(i);
  //   }
  // },
  components: {
    "v-stu-control": classStudentControl,
    "v-one-to-one-control": oneToOneControl,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-filter-select": FilterSelectBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    /**
    * 手动停课
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/11/11
     */
    stopClass () {
      if (this.stopClassIds.length > 0) {
        closeClass({
          class_id_list: this.stopClassIds
        }).then(res => {
          this.$message.success('结课成功')
          this.getClassList()
          this.stopClassIds = []
        }).catch(err => {
          this.$message.error('结课失败')
          this.stopClassIds = []
        })
      }
    },
    
    /**
    * 多选框
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/11/11
     */
    selectionChange (val) {
      this.stopClassIds = []
      val.forEach((item) => {
        this.stopClassIds.push(item.class_id)
      })
    },
    
    handleClick(tab, event) {
      console.log(tab, event);
    },
    toClassCalendar(){
      this.$router.push({path:"/course/class_calendar"})
    },
    filterChange(e, type) {
      if (type !== "page") this.page = 1;
      // 公共组件内设置的选'不限'是传0，这里吧0转''，方便后端查询
      if (e == 0) e = '';
      this[type] = e;
      this.getClassList();
    },
    getClassList() {
      let obj = {
        page: this.page,
        search: this.search,
        size: this.page_count,
        term: this.term,
        attend_type: this.attend_type,
        subject: this.subject,
        class_status: this.class_status,
        is_one_to_one: 0 // 0: 班课; 1: 一对一;
      };
      this.tableLoading = true;
      ClassList(obj)
        .then(res => {
          this.class_list =res.data.list;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(error => {
          this.tableLoading = false;
          this.$message.error(error);
        });
    },
    handleDetail(item) {
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
    handleEdit(item) {
      this.$router.push({
        name: "creat_class",
        query: {
          class_id: item.class_id,
          is_one_to_one: item.is_one_to_one,
          is_endTime: item.end_time,
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
            this.$message.success("删除成功");
            this.getClassList();
          }
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    //创建副本
    handleCopy(item) {
      classInfo({ class_id: item.class_id })
        .then(res => {
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
          this.$message.success("新增成功");
          this.getClassList();
        })
        .catch(e => {
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
      this.getClassList();
    },
    creatclass() {
      this.$router.push({
        name: "creat_class",
        query: {
          is_one_to_one: '0'
        }
      });
    },
    pageChange(val) {
      this.page = val;
      this.getClassList();
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData",
      courseTempList: state => state.course.courseTempList
    })
  },
  filters: {
    stuFormate(val) {
      if (val) {
        return val.replace(/,/g, "、");
      }
    },
    formatStatus (row, type) {
      let value = '';
      switch (row.class_status) {
        case "未上课":
          value = '1';
          break;
        case "在上课":
          value = '2';
          break;
        case "已结课":
          value = '3';
          break;
        default:
          value;
      }
      if(!type){
        let arr = {'1':'未上课', '2':'在上课', '3':'已结课'}
        return arr[value]?arr[value]:'未设置状态'
      }else{
        let typeArr = {'1':'success', '2':'warning', '3':'info'}
        return typeArr[value]?typeArr[value]:''
      }
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.el-tabs__nav-wrap
  padding: 0 60px !important;
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
.container-wrap >>> .el-tabs__nav-wrap
  padding-left: 30px;
  .el-tabs__item
    height: 60px;
    line-height: 60px;

</style>
