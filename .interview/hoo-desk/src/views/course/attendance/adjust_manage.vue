<template>
  <div>
    <v-table-wrap
      :page='page'
      :total="count"
      showSearch
      placeholder="校区、学生姓名、老师姓名"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="toLeave">添加请假</el-button>
      <template slot="searchItems">
        <v-radio-bar label="类别" @onChange="filterChange($event,'is_duty')" :radioList="dutyList"></v-radio-bar>
        <v-mutex-check-bar
          label="科目"
          :checkList="searchData.subject"
          @onChange="filterChange($event,'subject')"
        ></v-mutex-check-bar>
        <v-radio-bar
          label="操作"
          @onChange="filterChange($event,'is_remedy')"
          :radioList="remedyList"
        ></v-radio-bar>
        <v-time-bar :timeList="timeLabelList" @onChange="timeChange"></v-time-bar>
      </template>
      <template slot="table_title">补课列表</template>
      <!-- <el-button slot="table_btns" type="primary" @click="exportTable">导出列表</el-button> -->
      <el-table
        slot="table"
        @selection-change="selectChange"
        ref="tableRef"
        class="pub-table"
        :data="listData"
        v-loading="listLoading"
      >
        <el-table-column type="selection" :selectable="canSelect" width="55"></el-table-column>
        <el-table-column label="校区" prop="org_name"></el-table-column>
        <el-table-column label="学生姓名" prop="student_name"></el-table-column>
        <el-table-column label="班级" prop="class_name"></el-table-column>
        <el-table-column label="科目" prop="org_subject"></el-table-column>
        <el-table-column label="班级老师" prop="teacher_name"></el-table-column>
        <el-table-column label="课程日期" prop="attendance_date"></el-table-column>
        <el-table-column label="课时" prop="hours"></el-table-column>
        <el-table-column label="类别" prop="is_duty"></el-table-column>
        <el-table-column label="备注" prop="remark"></el-table-column>
        <el-table-column label="创建时间">
          <template slot-scope="scope">{{scope.row.update_date | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" width="160">
          <template slot-scope="scope">
            <template v-if="scope.row.is_remedy/1 !==0">
              <template v-if="scope.row.is_remedy / 1 ===1">
                <p>无需补课</p>
                <el-button type="text" @click="toAdjust(scope.row)">修改</el-button>
              </template>
              <template v-else-if="scope.row.attend_type / 1 ===2">
                <p style="text-align:left">已补课：{{scope.row.new_teacher_name}}</p>
                <p>{{scope.row.new_attendance_date}} {{scope.row.new_start_time}}</p>
                <p style="text-align:left">扣除课时：{{scope.row.used_times}}</p>
                <el-button type="text" @click="oneToAdjust(scope.row)">修改</el-button>
              </template>
              <template v-else>
                <p style="text-align:center">已补课：{{scope.row.new_teacher_name}}</p>
                <p>{{scope.row.new_attendance_date}} {{scope.row.new_start_time}}</p>
                <el-button type="text" @click="toAdjust(scope.row)">修改</el-button>
              </template>
            </template>
            <template v-else>
              <div v-if="scope.row.attend_type != 2">
                <el-button type="text" @click="toAdjust(scope.row)">补课</el-button>
                <el-button type="text" @click="noAdjust(scope.row)">无需补课</el-button>
              </div>
              <div v-else>
                <el-button type="text" @click="oneToAdjust(scope.row)">补课</el-button>
                <el-button type="text" @click="oneNoAdjust(scope.row)">无需补课</el-button>
              </div>
            </template>
          </template>
        </el-table-column>
        <div slot="append" v-if="listData.length !==0" class="table-footer">
          <div class="part-left">
            <el-button type="text" @click="selectAll">全选</el-button>
            <span>已选 {{selectArr.length}}</span>
          </div>
          <div class="part-right">
            <el-button type="text" @click="toAdjust('all')">批量补课</el-button>
            <el-button type="text" @click="noAdjust('all')">无需补课</el-button>
          </div>
        </div>
      </el-table>
    </v-table-wrap>
    <v-adjust-dialog
      @onRefresh="getList"
      :adjustIsArr="adjustIsArr"
      :info="adjustInfo"
      :is_byOrder="is_byOrder"
      @onClose="dialogClose(1)"
      :dialog="adjustShow"
    ></v-adjust-dialog>
    <v-leave-dialog @onRefresh="getList" @onClose="dialogClose(2)" :dialog="leaveShow"></v-leave-dialog>
    <el-dialog title="无需补课" width="500px" :visible.sync="noMakeUpdialog" @close="closeNoAdjust">
      <el-form
        :model="formData"
        ref="leaveForm"
        class="pub-form"
        label-width="120px"
      >
        <el-form-item label="扣除课时">
          <el-input type="Number" v-model="formData.class" @input="classChange(formData.class)"></el-input>
        </el-form-item>
        <el-form-item label="" >
          <div class="text-wrap">
            <p>当前学员剩余课时: <span class="blue-text">{{remaining_hours}}</span> 课时</p>
            <p>确认无需补课后, 将会扣除该学员 <span class="blue-text">{{formData.class == '' ? 0 : formData.class}}</span> 课时,</p>
            <p v-show="class_tips" class="red-text"><i>*</i> 学员剩余课时不足</p>
          </div>
        </el-form-item>
      </el-form>
      <div class="dialog-btn-bar" slot="footer">
        <el-button @click="closeNoAdjust">取消</el-button>
        <el-button type="primary" @click="saveNoAdjust">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import radioBar from "@/components/top_box/radio_bar";
import searchBar from "@/components/top_box/search_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import adjustDialog from "./adjust_dialog";
import leaveDialog from "./leave_dialog";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
import {
  createLeaves,
  getLeaveList,
  updateLeave,
  delLeave,
  getTimeList,
  getStudentList,
  getTeacherList,
  getLeaveDetails,
  subjeckList,
  setAdjusst,
  exportAdjustList,
  getUserCourseTime
} from "@/api/course_control";
export default {
  data() {
    return {
      statusList: [],
      listData: [],
      listLoading: false,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      selectArr: [], //需要批量处理的数组
      adjustShow: false,
      leaveShow: false,
      noMakeUpdialog: false,
      subject: "",
      is_duty: "",
      is_remedy: "",
      subject_list: [],
      dutyList: [],
      remedyList: [],
      adjustInfo: null,
      adjustIsArr: false,
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      datetime: ["", ""],
      formData: {
        class: "",
      },
      remaining_hours: 0,
      class_tips: false,
      oneData: [],
      is_byOrder: false // 是否是按次
    };
  },
  components: {
    "v-radio-bar": radioBar,
    "v-search-bar": searchBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-adjust-dialog": adjustDialog,
    "v-leave-dialog": leaveDialog,
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate
  },
  activated(){
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  computed:{
    ...mapGetters({
      searchData: "common/getSearchData",
      isNewType: "common/getSystemType"
    }),
  },
  methods: {
    /**
    * 获取剩余课时
    * getRemainingHours
    * @param  Boolean     {att_id}
     * Created by preference on 2019/09/24
     */
    getRemainingHours (item) {
      getUserCourseTime({att_id: item.att_id})
        .then(res => {
          console.log('%clogs','font-size:40px;color:pink;',res.data)
          this.remaining_hours = res.data.residue_time;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    /**
    * 课时
    * classChange
    * @param  Number     {value}
     * Created by preference on 2019/09/24
     */
    classChange (val) {
      if (val > this.remaining_hours) { // 输入扣除的课时 大于 剩余课时 则显示提示信息
        this.class_tips = true;
      } else {
        this.class_tips = false;
      }
    },

    exportTable() {
      this.$message.warning("订单导出中");
      exportAdjustList({
        search: this.search,
        is_duty: this.is_duty,
        is_remedy: this.is_remedy,
        subject: this.subject,
        start_time: this.datetime ? this.datetime[0] : "",
        end_time: this.datetime ? this.datetime[1] : ""
      })
        .then(res => {
          this.$downLoad(res.data);
          this.$message.success("导出成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    timeChange(val) {
      this.datetime = val;
      this.page = 1;
      this.getList();
    },
    canSelect(row, index) {
      return row.is_remedy / 1 === 0;
    },
    dialogClose(type) {
      if (type === 1) {
        this.adjustShow = false;
      } else {
        this.leaveShow = false;
      }
    },
    selectAll() {
      if (this.selectArr.length !== this.listData.length) {
        this.$refs.tableRef.toggleAllSelection();
      } else {
        this.$refs.tableRef.clearSelection();
      }
    },
    selectChange(list) {
      console.log(list);
      this.selectArr = list;
    },
    toLeave() {
      this.leaveShow = true;
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getLeaveList({
        page: this.page,
        size: this.size,
        search: this.search,
        is_duty: this.is_duty,
        is_remedy: this.is_remedy,
        subject: this.subject,
        start_time: this.datetime ? this.datetime[0] : "",
        end_time: this.datetime ? this.datetime[1] : ""
      })
        .then(res => {
          console.log("res", res);
          this.listData = res.data.list;
          this.getFilter(res.data);
          this.count = res.data.count / 1;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e, "error");
          this.listLoading = false;
        });
    },
    getFilter(item) {
      let keys = Object.keys(item.is_duty);
      let is_duty = keys.map(val => {
        return { label: item.is_duty[val], value: val };
      });
      keys = Object.keys(item.is_remedy);
      let is_remedy = keys.map(val => {
        return {
          label: `${item.is_remedy[val]}(${item.remedy_list[val]}条)`,
          orginLabel: item.is_remedy[val],
          value: val
        };
      });
      this.dutyList = is_duty;
      this.remedyList = is_remedy;
    },
    toAdjust(item) {
      if (item === "all") {
        if (this.selectArr.length === 0) {
          this.$message.warning("请选择需要批量操作的学生");
          return;
        }
        this.adjustIsArr = true;
        this.adjustInfo = this.selectArr;
      } else {
        this.adjustIsArr = false;
        this.adjustInfo = [item];
        this.is_byOrder = false; // 是否是按次
      }
      this.adjustShow = true;
    },
    noAdjust(item) {
      if (item === "all" && this.selectArr.length === 0) {
        this.$message.warning("请选择需要批量操作的学生");
        return;
      }
      this.$confirm('是否无需补课?', "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let att_ids = "";
          let edu_stu_ids = "";
          if (item === "all") {
            let att_idArr =[];
            let edu_stu_idArr = [];
            this.selectArr.forEach(i=>{
              att_idArr.push(i.att_id);
              edu_stu_idArr.push(i.edu_stu_id);
            })
            att_ids = att_idArr.join(",");
            edu_stu_ids = edu_stu_idArr.join(",");
          } else {
            att_ids = item.att_id;
            edu_stu_ids = item.edu_stu_id;
          }
          let data = {
            att_ids: att_ids,
            edu_stu_ids:edu_stu_ids,
            is_remedy: 1
          };
          return setAdjusst(data);
        })
        .then(res => {
          if (res) {
            this.$message.success("修改成功");
            this.getList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    /**
    * 按次收费 点击补课
    * oneToAdjust
    * @param  Boolean     {name}
     * Created by preference on 2019/09/24
     */
    oneToAdjust (item) {
      this.adjustIsArr = false; // 是否是批量
      this.adjustInfo = [item]; // 传当前条数据
      this.is_byOrder = true; // 是否是按次
      this.adjustShow = true; // 弹窗显示
    },
    /**
    * 按次收费 无需补课
    * oneNoAdjust
    * @param  Boolean     {name}
     * Created by preference on 2019/09/24
     */
    oneNoAdjust (item) {
      this.$confirm('是否无需补课?', "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          this.getRemainingHours(item); // 获取剩余课时
          this.oneData = item;
          this.noMakeUpdialog = true;
        })
    },
    closeNoAdjust () {
      this.noMakeUpdialog = false;
    },
    saveNoAdjust () {
      if (this.formData.class == '') {
        this.$message.error("请输入扣除课时");
        return;
      }else if (this.class_tips) {
        this.$message.error("学员剩余课时不足");
        return;
      }
      let att_ids = this.oneData.att_id;
      let edu_stu_ids = this.oneData.edu_stu_id;
      let data = {
        att_ids: att_ids,
        edu_stu_ids:edu_stu_ids,
        is_remedy: 1,
        attend_times: this.formData.class
      };
      setAdjusst(data)
        .then(res => {
          if (res) {
            this.$message.success("提交成功");
            this.getList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
      this.noMakeUpdialog = false;
    },
  },
  watch:{
    noMakeUpdialog: {
      handler(val){
        if (val == true) {
          this.formData.class = "";
        }
      },
      deep: true
    }
  }
};
</script>


<style lang="stylus" scoped>
.table-footer
  padding: 0 20px;
  display: flex;
  background: #f6f6f6;
  justify-content: space-between;
.text-wrap
  line-height 20px
</style>
