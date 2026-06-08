<template>
  <div class="index-wrap">
    <v-table-wrap
      :page="page"
      :total="count"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <!-- <el-button slot="table_btns" type="primary" @click="editClass">一键排课</el-button> -->
      <v-time-bar :status="1" slot="searchItems" label="时间" :timeList="timeLabelList" @onChange="timeChange"></v-time-bar>
      <el-table 
        slot="table" 
        v-loading="listLoading"
        ref="multipleTable"
        :data="listData"
        tooltip-effect="dark"
        style="width: 100%"
        class="pub-table"
      >
        <!-- @selection-change="handleSelectionChange" -->
        <el-table-column
          prop="teacher_name"
          label="教师名称"
          width="180">
        </el-table-column>
        <el-table-column
          prop="student_name"
          label="学员名称"
          width="180">
        </el-table-column>
        <el-table-column
          prop="class_name"
          label="班级名称">
          <template v-slot="scope">
            <span class="blue-text c-pointer" @click="jumpClassDetails(scope.row)">{{ scope.row.address }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="attendance_date"  
          label="考勤日期"
          width="180">
        </el-table-column>
        <el-table-column
          prop="attend_times"
          label="授课课时"
          width="180">
        </el-table-column>
        <el-table-column
          prop="price"
          label="课程单价">
        </el-table-column>
        <el-table-column
          prop="consume_amount"
          label="已消耗金额">
        </el-table-column>
        <el-table-column
          prop="remark"
          label="备注"
          width="180">
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import { getLessonsList } from "@/api/student_control";
export default {
  data () {
    return {
      count: 0,
      page: 1,
      page_count: 10,
      listData: [],
      timeLabelList: [],
      order_course_id: this.$route.query.order_course_id,
      listLoading: false,
    }
  },
  components: {
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate,
  },
  methods: {
    timeChange() {

    },
    /**
    * 获取课消课时列表
    * getList
    * @param  Number     {order_course_id}
     * Created by preference on 2019/09/18
     */
    getList() {
      this.listLoading = true;
      getLessonsList({order_course_id: this.order_course_id})
        .then(res => {
          console.log('%c获取课消课时列表','font-size:40px;color:pink;',res.data)
          this.listData = res.data.list;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("获取数据失败");
        });
    },
    /**
    * jumpClassDetails
    * 跳转班级详情页面
    * @param  Array     {row}
     * Created by preference on 2019/08/14
     */
    jumpClassDetails (row) {
      this.$router.push({
        path: "/course/class_detail",
        // query: {}
      })
    },
    
  },
  created () {
    this.getList();
  },
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap >>> .time-bar
  margin-bottom 0
.index-wrap >>> .filter-label
  margin-right 20px
</style>
