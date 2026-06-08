// 课程大纲
<template>
  <div class="index-wrap">
    <v-table-wrap
      :total="count"
      :page="page"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <div class="tips-wrap" slot="tips">
        <p class="tips-title">课程大纲</p>
        <p class="tips-content">机构可以将课程每一节课的上课内容在系统中录入，新增为课程大纲。当老师在发布课后点评时可直接选择大纲内容，大纲内容将直接显示在课后点评内容中，节省老师发布课后点评的书写工作量。数据中心-点评率功能模块可查看教师的点评率报表。</p>
      </div>
      <v-search-new-bar
        label="名称筛选"
        placeholder="课程名称、大纲名称"
        @onSearch="filterChange($event,'search')"
        slot="searchItems"
        :search="search"
        width="204px"
      ></v-search-new-bar>
      <!-- <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="筛选科目"
        :select-list="commonSearchList.subject"
        @onChange="filterChange($event,'source_id')"
        slot="searchItems"
      ></v-filter-select-bar>
      <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="筛选学期"
        :select-list="commonSearchList.term"
        @onChange="filterChange($event,'source_id')"
        slot="searchItems"
      ></v-filter-select-bar> -->
      <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="状态筛选"
        :select-list="statusList"
        @onChange="filterChange($event,'is_open')"
        slot="searchItems"
      ></v-filter-select-bar>
      <el-button type="primary" slot="table_btns" @click="createCourse">新增大纲</el-button>
      <el-table slot="table" v-loading="tableLoading" class="pub-table" :data="courseList">
        <el-table-column
          type="index"
          label="序号"
          width="50">
        </el-table-column>
        <el-table-column prop="name" label="大纲名称"></el-table-column>
        <el-table-column prop="course_info_num" label="内容数量"></el-table-column>
        <el-table-column prop="curriculum" label="课程范围"></el-table-column>
        <el-table-column label="状态">
          <template v-slot="scope">
            <el-tag
              :type="scope.row | formatStatus('tag')"
              slot="reference"
            >{{scope.row | formatStatus}}</el-tag>
            <!-- {{scope.row.is_open | formatStatus}} -->
          </template>
        </el-table-column>
        <el-table-column prop="create_uname" label="创建人"></el-table-column>
        <el-table-column class-name="table-btn-column" fixed="right" width="180" label="操作" >
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-outline-dialog
      @onClose="closeDialog($event)"
      :dialog="showDialog"
      :outlineId="outlineId"
    ></v-outline-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
import tableTemplate from "@/components/listViewTemplate";
import searchNewBar from "@/components/top_box/search_new_bar";
import filterSelectBar from "@/components/top_box/filter_select_bar";
import { getOutlineList, delCourse, createCourse, deleteOutline } from "@/api/group_course.js";
import { getCommonSearchParam } from "@/api/course_control";
import outlineDialog from "./outline_dialog";
export default {
  data () {
    return {
      page: 1,
      size: 10,
      count: 0,
      search: '',
      is_open: '',
      showDialog: false,
      tableLoading: false,
      outlineId: '',
      courseList: [],
      commonSearchList: [],
      statusList: [{attr_id: '0', attr_value: '不启用'},{attr_id: '1', attr_value: '启用'}]
    }
  },
  components: {
    "v-table-wrap": tableTemplate,
    "v-search-new-bar": searchNewBar,
    "v-filter-select-bar": filterSelectBar,
    'v-outline-dialog': outlineDialog,
  },
  methods: {
    /**
    * 关闭弹窗（页面所有公共弹窗组件公用方法）
    * closeDialog
    * @param  String     {data.type} 弹窗区分
     * Created by preference on 2019/10/16
     */
    closeDialog (data) {
      this.showDialog = false;
      this.getList();
      // this.getReportList();
    },
    /**
    * getCommonSearchList 获取公共筛选条件列表
     * Created by preference on 2019/12/05
     */
    getCommonSearchList () {
      getCommonSearchParam()
        .then(res => {
          this.commonSearchList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    /**
    * createCourse 新增大纲
     * Created by preference on 2019/12/05
     */
    createCourse () {
      this.outlineId = '';
      this.showDialog = true;
    },
    
    toEdit(item) {
      if (item.is_edit / 1 === 0) {
        this.$message.error('上课内容模板由上级分校创建，无权限修改');
        return;
      }
      this.showDialog = true;
      this.outlineId = item.id;
    },
    //删除课程
    toDel(item) {
      if (item.is_edit / 1 === 0) {
        this.$message.error('上课内容模板由上级分校创建，无权限删除');
        return;
      }
      this.$confirm("确定删除该课程大纲吗?", "提示")
        .then(() => deleteOutline({ id: item.id }))
        .then(res => {
          this.$message.success("删除成功");
          this.getList();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    /**
    * getList 获取列表数据
     * Created by preference on 2019/12/05
     */
    getList(){
      let obj = {
        page: this.page,
        count: this.count,
        size: this.size,
        name: this.search,
        is_open: this.is_open
      }
      getOutlineList(obj)
        .then(res => {
          let data = res.data.list;
          this.count = res.data.count / 1;
          this.courseList = data;
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
  },
  created () {
    this.getList();
    this.getCommonSearchList();
  },
  mounted () {
 /**
  *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
  *如果 root 实例挂载了一个文档内元素
  *当 mounted 被调用时 vm. 也在文档内。
  *页面添加滑动
 **/
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
  },
  filters:{
    formatStatus(row, type) {
      let value = "";
      switch (row.is_open) {
        case "0":
          value = "0";
          break;
        case "1":
          value = "1";
          break;
      }
      
      if (!type) {
        let arr = {
          "0": "不启用",
          "1": "启用",
        }
        return arr[value] ? arr[value] : "未知状态";
      } else {
        let typeArr = {
          "0": "info",
          "1": "success",
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    }
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.tips-wrap
  margin-bottom 20px
  .tips-title
    font-size 24px
    line-height 35px
    color $black
  .tips-content
    margin-top 15px
    width 742px
    font-size 14px
    line-height 20px
    color $gray
</style>
