<template>
  <div>
    <el-dialog 
      :visible.sync="dialogShow" 
      @close="close" 
      width="750px" 
    >
      <template slot="title">
        <el-row type="flex">
          <el-col style="font-size: 20px;">{{dialogTitle}}</el-col>
        </el-row>
      </template>
      <div class="temp-wrap">
        <div class="temp-list">
          <el-col :span="3">
            <span>已选学员</span>
          </el-col>
          <el-col :span="21">
            <ul class="student-list">
              <el-tag
                v-for="tag in studentTags"
                :key="tag.stu_id"
                closable
                type="info"
                height="35px"
                @close="handleClose(tag)"
              >
                {{tag.student_name}}
              </el-tag>
              <el-button @click="delStudentAll">删除全部</el-button>
            </ul>
          </el-col>
        </div>
        <div class="temp-list">
          <el-col :span="3">
            <span>搜索学员</span>
          </el-col>
          <el-col :span="10">
            <div class="filter-search">
              <el-col :span="18">
                <el-input class="search-input"
                          v-model="search"
                          @keyup.enter.native="searchStu(1)"
                          placeholder='输入学员姓名'></el-input>
              </el-col>
              <el-col :span="6">
                <el-button class="search-btn"
                          @click='searchStu(1)'
                          type="primary">搜索</el-button>
              </el-col>
            </div>
          </el-col>
          <el-col :span="11">
            <p class="hint"><i class="hoo hoo-feedback_fill"></i> 如列表未显示需要的学员, 可通过搜索查询</p>
          </el-col>
        </div>
      </div>
      <el-table
        ref="multipleTable"
        v-loading="loading"
        :data="listData"
        :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
        empty-text = "暂无数据" 
        tooltip-effect="dark"
        style="width: 100%"
        height="400"
        @selection-change="handleSelectionChange">
        <el-table-column
          type="selection"
          width="55">
        </el-table-column>
        <el-table-column
          prop="student_name"
          label="姓名"
          width="120">
        </el-table-column>
        <el-table-column
          label="收费类型"
          show-overflow-tooltip>
          <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
        </el-table-column>
        <el-table-column
          prop="course_name"
          label="课程名称"
          width="120">
        </el-table-column>
        <el-table-column
          prop="grade"
          label="年级"
          width="120">
        </el-table-column>
        <el-table-column
          label="剩余课时"
          width="120">
          <template slot-scope="scope">{{ scope.row['times']-scope.row['used_times'] }}</template>
        </el-table-column>
      </el-table>
      <el-button slot="footer" type="primary" @click="save">提交</el-button>
      <el-button slot="footer" @click="dialogShow = false">取消</el-button>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { getTemporaryStudent, setTemporaryStudent } from "@/api/class_control";
export default {
  data () {
    return {
      dialogShow: false,
      shouldRefresh: false,
      dialogTitle: '临时学员',
      listData: [],
      loading: false,
      search: "",
      studentTags: [],
      typeLabel: this.$store.getters.getAttendTypeLabel,
    }
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    classId: {
      type: [Number,String]
    },
    timetableId: {
      type: [Number,String]
    }
  },
  methods: {
    /**
    * handleClose
    * 删除已选中学员
    * @param  Object     {tag}
    * Created by preference on 2019/08/09
    */
    handleClose(tag) {
      this.studentTags.splice(this.studentTags.indexOf(tag), 1);
      this.$refs.multipleTable.toggleRowSelection(tag, false);
    },

    /**
    * handleClose
    * 关闭弹窗
    * @param  Object     {}
    * Created by preference on 2019/08/09
    */
    close() {
      this.$emit("onClose", this.shouldRefresh);
      this.studentTags = [];
      this.$refs.multipleTable.clearSelection();
    },

    /**
    * handleSelectionChange
    * 单选、全选
    * @param  Boolean     {name}
    * Created by preference on 2019/08/09
    */
    handleSelectionChange(val) {
      this.studentTags = val;
      console.log(val);
    },

    /**
    * delStudentAll
    * 删除所有选中的学员
    * @param  Array     {ids}
    * Created by preference on 2019/08/08
    */
    delStudentAll () {
      if (this.studentTags.length != 0) {
        this.studentTags = [];
        this.$refs.multipleTable.clearSelection();
        console.log('学员删除成功');
      }
    },

    /**
    * searchStu
    * 根据姓名搜索学生
    * @param  String     {student_name}
    * @param  Number     {type} 0：初始化进入；1：点击搜索
    * 由于数据量可能过多，所以初始进入时 默认搜索姓李的学员
    * Created by preference on 2019/08/09
    */
    searchStu (type) {
      let name
      if (type == 0) {
        name = '李'
        this.getTemporaryInfo(type, name);
      } else {
        this.getTemporaryInfo(type);
      }
    },

    /**
    * save
    * 保存已选学员（插班）
    * @param  Array     {order_course_id} 课程订单ID
    * @param  Array     {edu_stu_ids} 学生ID
    * @param  Array     {timetableId} 课程表ID
    * Created by preference on 2019/08/09
    */
    save () {
      let edu_stu_ids = [];
      let order_course_ids = [];
      this.studentTags.map( i => {
        edu_stu_ids.push(i.edu_stu_id);
        order_course_ids.push(i.order_course_id);
      })
      let obj = {
        order_course_id: order_course_ids,
        edu_stu_ids: edu_stu_ids,
        timetable_id: this.timetableId,
      }
      setTemporaryStudent(obj)
        .then(res => {
          console.log(res,'res');
          this.$message.success('插班成功');
          this.$refs.multipleTable.clearSelection();
          this.searchStu(0);
          this.dialogShow = false;
        })
        .catch(error => {
          console.log("error", error);
          this.$message.error(error);
        });
    },
    
    /**
    * getTemporaryInfo
    * 获取学员列表数据
    * @param  Number     {class_id}
    * @param  String     {student_name}
    * @param  Number     {type} 0：初始化进入；1：点击搜索
    * @param  String     {name}
    * 如果姓李的学员没有获取到数据，则会递归再获取一次姓王的学员
    * 如果搜索时为空则默认搜索姓李的学员
    * Created by preference on 2019/08/09
    */
    getTemporaryInfo (type, name) {
      this.loading = true;
      let obj
      let searchName = this.search;
      searchName = searchName == '' ? '李' : searchName;
      if (type == 0) {
        obj = {
          class_id: this.classId,
          student_name: name
        }
      } else {
        obj = {
          class_id: this.classId,
          student_name: searchName
        }
      }
      getTemporaryStudent(obj)
        .then(res => {
          console.log('%clistData','font-size:40px;color:pink;',res.data)
          this.listData = this.$copyObject(res.data);
          this.loading = false;
          if (type == 0) {
            if (res.data.length == 0 || res.data == '[]') {
              this.getTemporaryInfo(0, '');
            }
          }
        })
        .catch(error => {
          console.log("error", error);
          this.$message.error(error);
        });
    }
  },
  watch: {
      dialog() {
          if (this.dialog) {
            this.dialogShow = true;
            this.searchStu(0);
          }
      }
  }
}
</script>

<style lang="stylus" scoped>
.temp-list
  display flex
  margin-bottom 15px
  span 
    margin 0 15px 10px 0
    flex .3
    height 35px
    line-height 35px
    i 
      line-height 23px
  .student-list
    flex 2
  .student-name
    flex 2
  .hint
    // display flex
    font-size 14px
    color #8690ac
    line-height 35px
    i 
      // flex 1
      margin-right 5px
.search-btn
  height 36px
.filter-search >>> .el-input__inner
  border-radius: 2px 0 0 2px;
.filter-search >>> .el-button
  border-radius: 0 2px 2px 0;
</style>
