<template>
  <div class="index-wrap">
    <div class="header">
      <div class="header-left">
        <div class="header-left-list" style="margin-bottom: 30px;">
          <i v-if="nowList.is_one_to_one == 0">班</i>
          <i v-else>一</i>
          <span class="class-name">{{ nowList.class_name }}</span>
          <span class="class-label label-red">{{ nowList.org_subject }}</span>
          <span class="class-label label-orange">{{ nowList.org_grade }}</span>
          <span class="class-label label-green">{{ nowList.org_term }}</span>
        </div>
        <div class="header-left-list">
          <p>教师:
            <span>{{ nowList.teacher_name = nowList.teacher_name == '' ? '暂无' : nowList.teacher_name }}</span>
          </p>
          <p>
            <el-row>
              <el-col :span="5">
                助教:
              </el-col>
              <el-col :span="18">
                <span v-for="(item,index) in nowList.relation_teacher_name" :key="index">{{ item = item == '' ? '暂无' : item}}&nbsp;&nbsp;</span>
              </el-col>
            </el-row>
            </p>
          <p>教室: <span>{{ nowList.classroom_name = nowList.classroom_name == '' ? '暂无' : nowList.classroom_name }}</span></p>
          <p>开班人数: <span>{{ nowList.class_number }}</span></p>
        </div>
        <div class="header-left-list" style="margin-bottom: 0;">
          <p>备注: <span>{{ nowList.class_remark = nowList.class_remark == '' ? '暂无' : nowList.class_remark}}</span></p>
        </div>
      </div>
      <div class="header-right">
          <el-button slot="buttons" type="primary" @click="editClass">编辑班级</el-button>
      </div>
    </div>
    <el-tabs class="pane-wrap" v-model="activeName" @tab-click="handleClick">
      <el-tab-pane label="排课信息" name="course_info">
        <v-table-wrap
          :page="page"
          :total="count"
          @pageChange="filterChange($event,'page')"
          @sizeChange="filterChange($event,'size')"
        >
          <el-button slot="table_btns" type="primary" @click="editClass">一键排课</el-button>
          <el-button slot="table_btns" @click="delAttendance('all')">批量删除</el-button>
          <el-button slot="table_btns" @click="createClassTime">生成上课时间</el-button>
          <div slot="table_count" style="color: #3a3d57;" v-if="is_endTime == 0 && is_one_to_one == 0">
            规则排课 {{start_time}} 开始( <span class="gray-text" style="display: inline-block;" v-for="(item,index) in weekList" :key="index">{{item}}</span> )
          </div>
          <div slot="table_count" style="color: #3a3d57;" v-if="is_endTime != 0 && is_one_to_one == 0">
            日历排课：已排 <span style="color:#f8690a !important;">{{count}}</span> 次课
          </div>
          <template slot="table_title">考勤列表</template>
          <!-- <el-button @click="exportList" slot="table_btns" type="primary">导出课程表</el-button> -->
          <el-table
            slot="table"
            v-loading="listLoading"
            ref="multipleTable"
            :data="listData"
            tooltip-effect="dark"
            style="width: 100%"
            class="pub-table"
            @selection-change="handleDeleteChange"
          >
            <el-table-column
              type="selection"
              width="55">
            </el-table-column>
            <el-table-column label="课次" width="80px">
              <template slot-scope="scope">
                {{scope.$index + 1}}
              </template>
            </el-table-column>
            <el-table-column label="上课时间" width="240" prop="class_date" style="width: 250px;">
              <template
                slot-scope="scope"
              >{{scope.row.class_date + '(' + scope.row.start_time + '~' + scope.row.end_time + ')'}}</template>
            </el-table-column>
            <el-table-column label="教师" width="160" prop="teacher_name"></el-table-column>
            <el-table-column label="出勤状况">
              <template slot-scope="scope">
                <el-tag :type="scope.row | formatStatus('tag')">
                  <span>{{scope.row | formatStatus}}</span>
                  <span>{{scope.row.attendance}} / {{scope.row.student_count}}</span>
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240" class-name="table-btn-column">
              <template slot-scope="scope">
                <!-- 出勤大于1个，显示取消一键点名 scope.row.student_count / 1 !== 0 -->
                <el-button
                  :disabled="scope.row.isAfter"
                  type="text"
                  v-if="scope.row.student_count / 1 !== 0 || scope.row.attendance <= 0"
                  @click="setAllAttendance(scope.row)"
                >{{scope.row.attendance > 0 ? "取消点名" :'一键点名'}}</el-button>
                <el-button v-if="scope.row.attendance <= 0" type="text" @click="showDialogFunc(scope.row, 0)">点名</el-button>
                <el-button v-if="scope.row.attendance > 0" type="text" @click="showDialogFunc(scope.row, 1)">查看点名情况</el-button>
                <!-- v-if="scope.row.is_temporary == 1" -->
                <el-button
                  type="text"
                  @click="delAttendance('one', scope.row)"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </v-table-wrap>
      </el-tab-pane>
      <el-tab-pane label="班级成员" name="class_member">
        <v-table-wrap
          :page="pages"
          :total="counts"
          @pageChange="filterChanges($event,'pages')"
          @sizeChange="filterChanges($event,'size')"
        >
          <el-button slot="table_btns" type="primary" @click="openDialog" v-if="nowList.is_one_to_one == 0" style="margin-bottom: 10px;">添加学员</el-button>
          <el-button slot="table_btns" @click="delAll" v-if="nowList.is_one_to_one == 0" style="margin-bottom: 10px;">批量移除</el-button>
          <el-table
            slot="table"
            v-loading="dialogLoading"
            ref="multipleTable"
            :data="chooseStuList"
            tooltip-effect="dark"
            style="width: 100%;"
            class="pub-table"
            :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
            @selection-change="handleSelectionChange">
            <el-table-column
                type="selection"
                width="50"
                fixed="left">
              </el-table-column>
            <el-table-column
              label="排序"
              width="55">
              <template slot-scope="scope">{{ scope.$index + 1 }}</template>
            </el-table-column>
            <el-table-column
              label="学生姓名"
              width="120">
              <template slot-scope="scope">{{ scope.row.student_name }}</template>
            </el-table-column>
            <el-table-column
              prop="phone"
              label="手机号码"
              width="150">
            </el-table-column>
            <el-table-column
              prop="times"
              label="总课时"
              width="90"
              show-overflow-tooltip>
            </el-table-column>
            <el-table-column
              prop="surplus_times"
              label="剩余课时"
              show-overflow-tooltip>
            </el-table-column>
            <el-table-column label="操作" fixed="right" class-name="table-btn-column">
                <template slot-scope="scope">
                  <el-button
                    type="text"
                    @click="delStudent(scope.row)"
                  >移除学员</el-button>
                </template>
              </el-table-column>
          </el-table>
        </v-table-wrap>
      </el-tab-pane>
    </el-tabs>
    <el-dialog title="添加学员" width="500px" :visible.sync="dialogShow" @close="close">
      <el-select
        v-model="chooseStu"
        multiple
        style="width:400px"
        :filterable="true"
        default-first-option
        placeholder="请选择学生"
      >
        <el-option
          v-for="(item) in studentList"
          :label="item.student_name"
          :value="item.order_course_id"
          :key="item.order_course_id"
          style="display: flex"
        >
          <span style="flex:2;padding:0 5px">{{typeLabel[item.attend_type]}}</span>
          <span style="flex:3;padding:0 5px">{{item.student_name}}</span>
          <span style="flex:3;padding:0 5px">{{item.course_term}}</span>
          <span style="flex:2;padding:0 5px">{{item.grade}}</span>
          <span style="flex:2;padding:0 5px">{{item.subject_name}}</span>
          <span style="flex:2;padding:0 5px">{{item.surplus_hours}}</span>
        </el-option>
      </el-select>
      <el-button type="primary" slot="footer" @click="toAdd">保存</el-button>
      <el-button slot="footer" @click="close">取消</el-button>
    </el-dialog>
    <v-attendance
      @onClose="closeDialog"
      :classAttendTimes="bindAttendTimes"
      :id="bindId"
      :classId="bindClassId"
      :dialog="showDialog"
      :status="bindStatus"
      :items="items"
      :timetableId="bindId"
    ></v-attendance>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import {
  curriculumList,
  setAllStudentAttendance
} from "@/api/course_control";
import { classInfo, studentList, addStudent, periodicTable, deleteClassTimetable, createClassTimetable} from "@/api/class_control";
import { userList } from "@/api/school_control";
import { delStu } from "@/api/student_control";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import AttendanceDialog from "./attendance/attendance_dialog";
import { mapGetters } from "vuex";
export default {
  data () {
    return {
      class_id: this.$route.query.class_id,
      nowList: [],
      activeName: 'course_info',
      count: 0,
      page: 1,
      page_count: 10,
      counts: 0,
      pages: 1,
      page_counts: 10,
      listData: [],
      class_list: [],
      teacher_list: [],
      tableLoading: false,
      listLoading: false,
      dialogLoading: false,
      dialogShow: false,
      studentList: [],
      chooseStu: [],
      chooseStuList: [],
      multipleSelection: [],
      courseInfoSelection: [],
      bindId: "",
      bindAttendTimes: 1,
      bindClassId: "",
      bindStatus: 0,
      showDialog: false,
      start_time: '',
      weekList: [],
      items: [],
      is_endTime: this.$route.query.is_endTime,
      is_one_to_one: this.$route.query.is_one_to_one
    }
  },
  components: {
    "v-attendance": AttendanceDialog,
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate,
  },
  created() {
    // 新版不请求
    this.getList();
    this.getTeacherList(); // 获取教师列表
    this.getClassInfo(); // 获取当前班级信息
    this.getPeriodicTable(); // 获取规则排班数据
  },
  methods: {
    /**
    * 手动生成上课时间
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/11/10
     */
    createClassTime () {
      console.log('%cthis.$router.query','font-size:40px;color:pink;',this.$route.query.class_id)
      let class_id = this.$route.query.class_id
      let weekList = this.$getWeek()
      let start_date = this.$formatToDate(weekList[0]._d.valueOf() / 1000, "Y-M-D")
      let end_date = this.$formatToDate(weekList[1]._d.valueOf() / 1000, "Y-M-D")
      createClassTimetable({
        only_old: 1,
        class_id,
        start_date,
        end_date
      }).then(res => {
        console.log('%cres','font-size:40px;color:pink;',res)
        this.getList()
      }).catch(err => {
        console.log('%cerr111','font-size:40px;color:pink;',err)
      })
    }, 
    
    /**
    * delAttendance 批量删除排课信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/22
     */
    delAttendance (type, row) {
      let obj = {}
      let ids = [];
      if (type == 'all') {
        this.courseInfoSelection.forEach(item => {
          ids.push(item.id)
        })
        obj = {
          class_id: this.class_id,
          ids: ids
        }
      } else {
        ids.push(row.id);
        obj = {
          class_id: this.class_id,
          ids: ids
        }
      }
      // deleteClassTimetable
      this.$confirm("此操作将删除选中的排课信息, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteClassTimetable(obj);
        })
        .then(res => {
          this.$message.success('删除成功');
          this.getList();
        }).catch(error => {
          this.$message.error(error);
        });
    },  
    
    openDialog(){
      this.dialogShow = true;
    },
    close() {
      this.chooseStu = [];
      this.dialogShow = false;
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      if (type === "subject") {
        let value = val.length > 0 ? val.split(",") : "";
        value = JSON.stringify(value);
        this[type] = value;
      } else {
        this[type] = val;
      }
      this.getList();
    },
    filterChanges(val, type) {
      if (type !== "page") this.page = 1;
      if (type === "subject") {
        let value = val.length > 0 ? val.split(",") : "";
        value = JSON.stringify(value);
        this[type] = value;
      } else {
        this[type] = val;
      }
      this.getClassAndStuList();
    },
    getPeriodicTable() {
      periodicTable({ class_id: this.class_id }).then(res => {
        let data = res.data;
        console.log('%cres.data','font-size:40px;color:pink;',res.data)
        // this.start_time = this.timestampToTime(data.start_time);
        if (data.rule != null) {
          this.start_time = data.start_time | formatToDate("Y-M-D");
          let weekList = [];
          let rule = data.rule;
          // let week = JSON.stringify(data.rule);
          for (let i = 0; i < rule.length; i++) {
            weekList.push(rule[i].day);
          }
          this.weekList = weekList;
        }
      }).catch(error => {
        this.$message.error(error);
      });
    },
    // 时间戳转日期格式
    // timestampToTime(timestamp) {
    //   var date = new Date(timestamp * 1000);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
    //   var Y = date.getFullYear() + '-';
    //   var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
    //   var D = (date.getDate() < 10 ? '0'+date.getDate() : date.getDate()) + ' ';
    //   //  var h = (date.getHours() < 10 ? '0'+date.getHours() : date.getHours()) + ':';
    //   //  var m = (date.getMinutes() < 10 ? '0'+date.getMinutes() : date.getMinutes()) + ':';
    //   //  var s = (date.getSeconds() < 10 ? '0'+date.getSeconds() : date.getSeconds());
    //   return Y+M+D;
    // },
    // 选择学员
    handleSelectionChange(val) {
      console.log('%cmultipleSelection','font-size:40px;color:pink;',val)
      this.multipleSelection = val;
    },
    /**
    * handleDeleteChange 批量删除排课信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/22
     */
    handleDeleteChange (val) {
      console.log('%ccourseInfoSelection','font-size:40px;color:pink;',val)
      this.courseInfoSelection = val
    },
    
    showDialogFunc(item, status) {
      this.showDialog = true;
      this.bindAttendTimes = item.attend_times;
      this.bindId = item.timetable_id;
      this.bindClassId = item.class_id;
      this.items = item;
      this.bindStatus = status;
    },
    closeDialog(status) {
      this.showDialog = false;
      this.bindAttendTimes = 0;
      if (status) this.getList();
    },
    // 添加学员
    toAdd() {
      if (this.chooseStu.length == 0) {
        this.$message.error("请选择学生后再添加");
        return;
      }
      let obj = {
        class_id: this.class_id,
        student_list: JSON.stringify(this.chooseStu)
      };
      this.dialogLoading = true;
      addStudent(obj)
        .then(res => {
          this.$message.success("添加学生成功");
          this.dialogShow = false;
          this.chooseStu = [];
          this.getClassAndStuList();
          this.dialogLoading = false;
        })
        .catch(e => {
          this.dialogLoading = false;
          this.$message.error(e);
        });
    },
    // 批量移除学员
    delAll() {
      if (this.multipleSelection != [] && this.multipleSelection != '' && this.multipleSelection.length != 0) {
        this.$confirm("此操作将移除选中的学生, 是否继续?", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning"
        })
          .then(() => {
            let ids = this.multipleSelection.map(val => {
              return val.edu_stu_id;
            });
            let obj = {
              student_ids: JSON.stringify(ids)
            };
            return delStu(obj);
          })
          .then(res => {
            this.$message.success("删除成功");
            this.getClassAndStuList();
          })
          .catch(e => {
            if (e != "cancel") {
              this.$message.error(e);
            }
          });
      } else {
        this.$message({
          message: '请勾选需要移除的学员',
          type: 'warning'
        });
      }
    },
    // 移除学员
    delStudent(item) {
      this.$confirm("此操作将移除该学生, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            student_ids: JSON.stringify([item.edu_stu_id])
          };
          return delStu(obj);
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.getClassAndStuList();
          }
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    // nav 点击切换 更新数据
    handleClick(tab, event) {
      if (tab.label == '排课信息') {
        this.getClassInfo();
      } else {
        this.getClassAndStuList(); // 获取班级成员列表
      }
    },
    editClass() {
      this.$router.push({
        name: "creat_class",
        query: {
          class_id: this.class_id,
          is_endTime: this.is_endTime,
          is_one_to_one: this.is_one_to_one,
        }
      });
    },
    getList() {
      this.listLoading = true;
      // 默认查从2010-01-01开始到今年的五年后的01-01.
      let date = new Date();
      let start_time = '2010-01-01'
      let end_time = date.getFullYear() + 5;
      start_time = new Date(start_time).getTime() / 1000;
      end_time = end_time + '-01-01';
      end_time = new Date(end_time).getTime() / 1000;
      let obj = {
        class_id: this.class_id,
        search: this.search,
        page: this.page,
        size: this.size,
        start_time: start_time,
        end_time: end_time,
      };
      curriculumList(obj)
        .then(res => {
          this.count = res.data.count / 1;
          let list = res.data.list;
          let nowTime = new Date().setHours(0, 0, 0, 0);
          list.forEach(item => {
            let compareTime = new Date(item.class_date).setHours(0, 0, 0, 0);
            item.isAfter = compareTime - nowTime > 0 ? true : false;
          });
          this.listData = list;
          this.listLoading = false;
        })
        .catch(e => {
          this.listLoading = false;
        });
    },
    getClassInfo() {
      // is_one_to_one: 0; 普通排班、is_one_to_one: 0; 一对一排班
      // is_endTime: 0; 规则排课、is_endTime: 时间戳; 日历排课
      // class_category： 一对一：one_to_one； 规则排课：rule_class； 日历排课：ordinary
      let class_category = '';
      if (this.is_one_to_one == '0') {
        if (this.is_endTime == '0' || this.is_endTime == 0 || this.is_endTime == '') {
          class_category = 'rule_class'
        } else {
          class_category = 'ordinary'
        }
      } else {
        class_category = 'one_to_one'
      }
      classInfo({ class_id: this.class_id, class_category: class_category })
        .then(res => {
          let class_info = res.data;
          class_info.relation_teacher = this.$copyObject(class_info.relation_teacher_ids);
          let teacherList = this.teacher_list;
          if (teacherList.length == 0) {
            setTimeout(() => {
              this.filterTeacher(class_info);
            }, 1000);
          } else {
            this.filterTeacher(class_info);
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    filterTeacher (class_info) {
      let relation_teachers = [];
      for (let i = 0; i < this.teacher_list.length; i++) {
        if (class_info.teacher_id == this.teacher_list[i].user_id) {
          class_info.teacher_name = this.teacher_list[i].nickname;
        }
        for (let j = 0; j < class_info.relation_teacher_ids.length; j++) {
          if (class_info.relation_teacher_ids[j]  == this.teacher_list[i].user_id) {
            relation_teachers.push(this.teacher_list[i].nickname);
          }
        }
      }
      class_info.relation_teacher_name = relation_teachers;
      this.start_time = this.$formatToDate(class_info.start_time, "Y-M-D");

      let weekList = [];
      // let week = JSON.stringify(data.rule);
      for (let i = 0; i < class_info.week_list.length; i++) {
        weekList.push(class_info.week_list[i].day);
      }
      this.weekList = weekList;
      this.nowList = class_info;
    },
    /**
    * getClassAndStuList
    * 获取学员列表信息
    * @param  Number     {class_id}
     * Created by preference on 2019/07/31
     */
    getClassAndStuList () {
      this.dialogLoading = true;
      classInfo({ class_id: this.class_id })
        .then(res => {
          console.log('%clogs','font-size:40px;color:pink;',res.data)
          let list = res.data.student_list.concat(res.data.closed_list);
          list.forEach(item => {
            item.totalClassHours = item.times * item.hours;
            item.remainingClassHours = item.used_times * item.hours;
          });
          this.chooseStuList = list;
          this.counts = list.length;
          let type = [2, 3].includes(res.data.attend_type / 1)
            ? "2,3"
            : res.data.attend_type;
          let obj = {
            page: this.pages,
            size: this.size,
            has_class: 1,
            subject_name: res.data.org_subject,
            attend_type: type
          };
          return studentList(obj);
        })
        .then(res => {
          let list = res.data.list;
          // 已排班学生列表的去除本班学生
          // if (this.stuStatus) {
          //   list = list.filter(
          //     i =>
          //       !this.hasStuList.some(
          //         _i => _i.stu_id === i.stu_id && _i.edu_stu_id === i.edu_stu_id
          //       )
          //   );
          // }
          // this.stuListMap.set(this.stuStatus, { status: true, list: list });
          this.studentList = list;
          this.dialogLoading = false;
        })
        .catch(e => {
          this.dialogLoading = false;
        });
    },

    getTeacherList() {
      let obj = {
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          this.teacher_list = res.data.list.filter((val, index) => {
            return val.status === "1";
          });
          let arr = [];
          this.teacher_list.forEach(item => {
            arr.push(item.user_id);
          });
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    setAllAttendance(item) {
      if (item.student_count <= 0) {
        this.$message.warning("请选择学生进行考勤");
        return;
      }
      // 出勤大于1个，取消一键点名
      let is_duty = item.attendance > 0 ? 0 : 1;
      setAllStudentAttendance({ timetable_id: item.id, is_duty, attend_times: item.default_times })
        .then(res => {
          this.$message.success("一键点名成功");
          this.getList();
        })
        .catch(e => {
          (e);
          this.$message.error(e);
        });
    }
  },
  computed: {
    typeLabel: function() {
      return this.$store.getters.getAttendTypeLabel;
    },
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
    relationTeacher() {
      if (this.teacher_list.length == 0) return [];
      return this.teacher_list.filter(i => i.user_id !== this.nowList.teacher_id);
    },
    dateTime: function() {
      let date = new Date();
      let start_time = '2010-01-01'
      let end_time = date.getFullYear() + 5;
      start_time = new Date(start_time).getTime() / 1000;
      end_time = end_time + '-01-01';
      end_time = new Date(end_time).getTime() / 1000;
      return [start_time, end_time]
    }
  },
  filters: {
    formatStatus (row, type) {
      let value
      if(row.attendance>0){
        // if(row.absence>0){
        //   value = '0'
        // }
        value = '0'
      }else{
        value = '1'
      }
      let time = new Date(Date.parse(row.class_date.replace(/-/g,  "/"))).getTime()
      let now = new Date().getTime()
      if(time-now>=0){
        value = '2'
      }
      if(!type){
        let arr = {'0':'已考勤', '1':'未考勤', '2':'未上课'}
        return arr[value]?arr[value]:'未知状态'
      }else{
        let typeArr = {'0':'warning', '1':'danger','2':'success'}
        return typeArr[value]?typeArr[value]:''
      }
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap >>> .el-tabs__nav-wrap
  padding-left 30px
  .el-tabs__item
    height 60px
    line-height 60px
.header
  display flex
  border-bottom 10px solid #f6f8fb
  padding 20px 30px
  .header-left
    flex 1
    .header-left-list
      margin-bottom 20px
      line-height 20px
      &:nth-child(1)
        i
          display inline-block
          margin-right 5px
          border-radius 50%
          width 30px
          line-height 30px
          color #0084ff
          background #eaf0f8
          text-align center
        span
          margin-right 5px
          vertical-align middle
        .class-name
          font-size 20px
        .class-label
          display inline-block
          border-radius 2px
          padding 0 18px
          font-size 12px
          line-height 24px
          color #fff
          text-align center
        .label-red
          background #f86b6e
        .label-orange
          background #fd9161
        .label-green
          background #4cd663
      &:nth-child(2)
        display flex
        p
          flex 1
      &:nth-child(3)
        line-height 20px
  .header-right
    flex .5
    text-align right
.pane-wrap >>> .pub-filter-box
  padding 0
.pane-wrap >>> .border
  border-bottom 0px solid #f6f8fb !important
.pane-wrap >>> .el-tabs__header
  margin 0
.pane-wrap >>> .pub-table-wrap
  padding 0 20px 10px 20px
</style>
