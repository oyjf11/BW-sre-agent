// 考勤弹窗
<template>
  <div>
    <el-dialog
      :visible.sync="dialogShow"
      @close="close"
      width="820px"
    >
      <template slot="title">
        <el-row type="flex">
          <el-col style="font-size: 20px;">{{dialogTitle}}</el-col>
          <!-- <el-col style="flex:1">{{className}}</el-col> -->
          <!-- <el-col
            style="flex:0 0 auto;width:auto;margin-left:10px;text-align:right;margin-right:30px"
          >{{attendanceNum}}</el-col> -->
        </el-row>
      </template>
      <div class="header">
        <div class="header-left">
          <div class="header-left-list">
            <i v-if="nowList.is_one_to_one == 0">班</i>
            <i v-else>一</i>
            <span class="class-name">{{ nowList.class_name }}</span>
            <span class="class-label label-red" v-if="nowList.org_subject">{{ nowList.org_subject }}</span>
            <span class="class-label label-orange" v-if="nowList.org_grade">{{ nowList.org_grade }}</span>
            <span class="class-label label-green" v-if="nowList.org_term">{{ nowList.org_term }}</span>
          </div>
          <div class="header-left-list-wrap">
            <div v-if="infoData!==null" class="header-list-left">
              <p>上课时间: {{ infoData.class_date }} <span style="color: #8690ac;">{{ '(' + infoData.start_time + '~' + infoData.end_time + ')' }}</span></p>
              <!-- <p v-else>上课时间: <span>{{ nowList.start_time | formatToDate("Y-M-D") }}</span></p> -->
            </div>
            <div class="header-list-right">
              {{attendanceNum}}
            </div>
          </div>
        </div>
      </div>
      <div class="pub-table-wrap">
        <div class="top-bar">
          <div class="label">授课老师:</div>
          <el-select v-model="teacher_id" v-if="status != 1">
            <el-option
              :value="item.teacher_id == 0 ? '暂无数据' : item.teacher_id"
              :label="item.teacher_name"
              v-for="(item,index)  in teacherList"
              :key="index"
            ></el-option>
          </el-select>
          <span style="line-height: 35.5px;" v-else>{{showTeacher}}</span>
          <div class="img-box">
            <el-button @click="showTemporaryDialogFunc">+ 临时学员</el-button>
            考勤图片 :&nbsp;
            <span v-if="!zoomPath">无</span>
            <el-button v-else type="text" class="can-click" @click="zoomShow = true;">查看</el-button>
          </div>
        </div>
        <el-table
          border
          height="400"
          :data="listData"
          v-loading="listLoading"
          style="margin:10px auto 0"
          class="pub-table"
        >
          <!-- <el-table-column label="序号" width="50" type="index"></el-table-column> -->
          <el-table-column label="学生姓名" prop="student_name"></el-table-column>
          <el-table-column width="180">
            <template slot="header">出勤状态
              <el-button
                @click="allToAttendance"
                style="margin-left:20px"
                type="text"
                v-if="status != 1"
              >{{attendanceText}}</el-button>
            </template>
            <template slot-scope="scope">
              <div v-if="status != 1 || scope.row.is_edit">
                <el-switch
                  v-if="!scope.row.isAbsence"
                  v-model="scope.row.is_dutys"
                  @change="changeAttendance($event,scope.row)"
                  active-text="出勤"
                  :disabled="isAfter"
                  inactive-text="缺勤"
                ></el-switch>
                <el-switch
                  v-if="scope.row.isAbsence"
                  v-model="scope.row.isAbsence"
                  disabled
                  active-text="请假"
                ></el-switch>
              </div>
              <div v-else>
                <el-tag :type="scope.row | formatStatus('tag')">
                  <span>{{scope.row | formatStatus}}</span>
                </el-tag>
                <!-- <span v-if="scope.row.is_duty"> 出勤 </span>
                <span v-else>缺勤</span> -->
              </div>
            </template>
          </el-table-column>
          <el-table-column width="130" v-if="showAttendTimes">
            <template slot="header">授课课时
              <el-button
                type="text"
                style="margin-left:10px"
                @click="openTimeDialog"
                v-if="status != 1"
              >修改</el-button>
            </template>
            <template slot-scope="scope">
              <el-input-number
                style="width:100%"
                :step="0"
                :min="0"
                :precision="2"
                :controls="false"
                placeholder="请输入授课课时"
                v-model="scope.row.attend_times"
                v-if="status != 1 || scope.row.is_edit"
              ></el-input-number>
              <span v-else>{{scope.row.attend_times}}</span>
            </template>
          </el-table-column>
          <el-table-column label="剩余课时" width="100">
            <!-- <template slot-scope="scope" >{{scope.row.times - scope.row.used_times}}</template> -->
            <template slot-scope="scope" >{{scope.row.course_times}}</template>
          </el-table-column>
          <!-- <el-table-column label="联系人">
            <template slot-scope="scope">{{scope.row.contacts[0].name}}</template>
          </el-table-column> -->
          <el-table-column label="联系电话">
            <template slot-scope="scope">{{scope.row.contacts[0].phone}}</template>
          </el-table-column>
          <el-table-column label="备注" prop="remark"></el-table-column>
          <el-table-column width="160" fixed="right">
            <template slot-scope="scope">
              <el-popover placement="top" width="150" trigger="click" @hide="popoverHide">
                <el-input v-model="remark" placeholder="请输入备注"></el-input>
                <div style="text-align:center;margin-top:10px;">
                  <el-button type="primary" style="martin-top" @click="addRemark(scope.row)">提交</el-button>
                </div>
                <!-- :disabled="remarkStatus[scope.$index]" -->
                <el-button type="text" slot="reference">添加备注</el-button>
              </el-popover>
              <el-button type="text" v-if="scope.row.is_temporary == 1" @click="deleteList(scope.row)">删除</el-button>
            </template>
          </el-table-column>
          <el-table-column width="120" label="操作" v-if="status == 1">
            <template slot-scope="scope">
              <span class="edit-btn" @click="editOneList(scope)">{{!scope.row.is_edit ? '修改' : '提交修改'}}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-button v-if="status != 1" type="primary" slot="footer" @click="save(0)">提交</el-button>
      <el-button v-if="status != 1" slot="footer" @click="dialogShow=false">取消</el-button>
    </el-dialog>
    <el-dialog :visible.sync="zoomShow">
      <img width="100%" :src="zoomPath">
    </el-dialog>
    <el-dialog width="280px" title="设置课时" :visible.sync="timeDialog">
      <el-input-number
        :step="0"
        :min="0"
        :precision="2"
        controls-position="right"
        v-model="allTimes"
      ></el-input-number>
      <el-button slot="footer" type="primary" @click="setAllTimes">保存</el-button>
      <el-button slot="footer" @click="timeDialog = false">取消</el-button>
    </el-dialog>
    <v-temprary-dialog
      @onClose="closeDialog"
      :dialog="showTemporaryDialog"
      :classId="class_id"
      :timetableId="timetable_id"
    ></v-temprary-dialog>
  </div>
</template>
<script>
import {
  getClassAttendanceInfo,
  setStudentAttendance
} from "@/api/course_control";
import { classInfo, deleteTemporaryTimetable } from "@/api/class_control";
import TempraryDialog from "./temporary_dialog";
export default {
  data() {
    return {
      dialogShow: false,
      listData: [],
      remark: "",
      type: 0, // 2 出勤表打开  其他 课程表打开
      listLoading: false,
      shouldRefresh: false,
      leave: 0,
      zoomShow: false,
      zoomPath: "",
      infoData: null,
      attend_times: 1,
      showAttendTimes: true,
      allTimes: 0,
      timeDialog: false,
      allAttendance: false,
      teacher_id: "",
      teacherList: [],
      nowList: [],
      classTime: {},
      dialogTitle: '点名',
      showTemporaryDialog: false,
      class_id: '',
      timetable_id: '' // 课程表ID
    };
  },
  components: {
    'v-temprary-dialog': TempraryDialog
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    dialogType: {
      // 2 出勤表打开  其他 课程表打开
      type: Number,
      default: 0
    },
    classId: { type: null },
    status: { type: null },
    id: { type: null },
    items: {type: null},
    timetableId:null
  },
  methods: {
    /**
    * deleteList 删除临时插班进入的学员
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/23
     */
    deleteList (row) {
      this.$confirm("此操作将会删除该学员, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteTemporaryTimetable({ att_id: row.att_id });
        })
        .then(res => {
          this.$message.success('删除成功');
          this.getList();
        }).catch(error => {
          this.$message.error(error);
        });
    },
    
    /**
    * closeDialog
    * 关闭临时插班学员弹窗
    * @param  Boolean     {name}
     * Created by preference on 2019/08/08
     */
    closeDialog () {
      this.showTemporaryDialog = false;
      this.getList();
    },
    /**
    * showTemporaryDialogFunc
    * 临时插班弹窗
    * @param  Boolean     {name}
     * Created by preference on 2019/08/08
     */
    showTemporaryDialogFunc () {
      this.showTemporaryDialog = true;
      this.class_id = this.classId;
      console.log('%cthis.items','font-size:40px;color:pink;',this.items)
      console.log('%cthis.timetableId','font-size:40px;color:pink;',this.timetableId)
      this.timetable_id = this.items.timetable_id;
      if (this.timetable_id === undefined) {
        this.timetable_id = this.timetableId
      }
    },

    /**
    * getClassInfo
    *
    * 获取班级详情信息
    *
     * Created by preference on 2019/08/08
     */
    getClassInfo () {
      classInfo({ class_id: this.classId })
        .then(res => {
          let class_info = res.data;
          class_info.start_time = Number(class_info.start_time);
          this.nowList = class_info;
        })
        .catch(error => {
          console.log("error", error);
          this.$message.error(error);
        });
    },

    editOneList(scope) {
      scope.row.is_edit = !scope.row.is_edit;

      this.$set(scope.row, scope.row.$index, {is_edit: scope.row.is_edit});
      if (scope.row.is_edit == false) {
        this.save(1);
      }
    },

    save(t) {
      let preList = this.infoData.list;
      let list = this.listData;
      // 按次缺勤算入补课的 不过滤
      // if (!this.timeAsLeave) {
      //   list = list.filter((i, index) => {
      //     let { is_duty, remark, attend_times } = preList[index];
      //     //去除请假学生
      //     if (i.isAbsence) return true;
      //     //现在状态为缺勤，不需要判断时间跟备注
      //     if (i.is_duty == 0) return i.is_duty !== is_duty;
      //     return (
      //       i.is_duty !== is_duty ||
      //       i.remark !== remark ||
      //       i.attend_times / 1 !== attend_times / 1
      //     );
      //   });
      // }
      list.forEach(item => {
        //是否请假
        if (item.isAbsence) {
          item.is_duty = 2;
        }
        if (item.is_duty == 2) {
          item.is_duty = 2;
        } else {
          item.is_duty = item.is_dutys ? 1 : 0
        }
      });
      list = list.map(i => ({
        edu_stu_id: i.edu_stu_id,
        times: i.attend_times,
        remark: i.remark,
        is_duty: i.is_duty
      }));
      if (list.length !== 0) {
        let item = list.find(i => !i.times && i.times / 1 !== 0);
        if (item) {
          item = this.listData.find(i => i.edu_stu_id === item.edu_stu_id);
          this.$message.error(`${item.student_name}的授课课时不能为空或者0`);
          return;
        }
        let params = {
          timetable_id: this.timetable_id,
          teacher_id: this.teacher_id,
          attendance_info: JSON.stringify(list),
          post_all: this.timeAsLeave ? "1" : "0"
        };
        setStudentAttendance(params)
          .then(res => {
            this.shouldRefresh = true;
            if (t == 0) this.dialogShow = false;
            this.$emit("onClose", this.shouldRefresh);
            this.$message.success("考勤修改成功");
          })
          .catch(e => this.$message.error(e));
      } else {
        this.dialogShow = false;
      }
    },
    openTimeDialog() {
      if (this.isAfter) return;
      // this.dialogShow = true;
      this.timeDialog = true;
    },
    setAllTimes() {
      this.listData.forEach(i => (i.attend_times = this.allTimes));
      this.timeDialog = false;
    },
    close() {
      this.teacher_id = "";
      this.teacherList = [];
      this.$emit("onClose", this.shouldRefresh);
    },
    getList() {
      let obj;
      obj = {
        postType: 1,
        timetable_id: this.id,
        class_id: this.classId
      };
      this.listLoading = true;
      getClassAttendanceInfo(obj)
        .then(res => {
          let list = res.data.list;
          list.forEach(item => {
            //是否请假
            item.isAbsence = item.is_duty / 1 === 2;
            // item.is_duty = item.is_duty / 1 === 1;
            item.is_duty = Number(item.is_duty);
            item.is_dutys = item.is_duty / 1 === 1;
            if (!item.contacts[0]) {
              item.contacts[0] = { name: "", phone: "" };
            }
            item.attend_times = item.attend_times || res.data.attend_times;
            item.is_edit = false;
          });
          this.teacherList = res.data.teacher;
          // attend_teacher_id 返回不为0 则取当前attend_teacher_id的值为授课教师显示的值
          if (Number(res.data.attend_teacher_id) != 0) {
            this.teacher_id = res.data.attend_teacher_id;
          } else {
            this.teacher_id = res.data.teacher[0].teacher_id == 0 ? '' : res.data.teacher[0].teacher_id;
          }
          this.allAttendance = res.data.attendance > 0;
          this.leave = res.data.leave / 1;
          this.zoomPath = res.data.image_path;
          this.listData = this.$copyObject(list);
          this.infoData = res.data;
          this.showAttendTimes = res.data.attend_type / 1 === 2;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    changeAttendance(val, item) {
      let status = this.listData.some(i => i.is_duty === true);
      this.allAttendance = status;
    },
    allToAttendance() {
      if (this.isAfter) return;
      this.allAttendance = !this.allAttendance;
      this.listData.forEach(i => {
        i.is_dutys = this.allAttendance;
      });
    },
    addRemark(item) {
      item.remark = this.remark;
    },
    popoverHide() {
      this.remark = "";
    }
  },
  computed: {
    // 备注状态
    remarkStatus() {
      let type = this.infoData.attend_type / 1;
      let list = this.listData.map(i => {
        if (this.timeAsLeave) return this.isAfter || i.isAbsence;
        return (
          this.isAfter || i.isAbsence || (type === 2 && i.is_duty === false)
        );
      });
      return list;
    },
    showTeacher() {
      let teacherName = '';
      let teacherNameList = this.teacherList.map(i => {
        if (this.teacher_id == i.teacher_id) {
          return(
            i.teacher_name
          );
        }
      })
      teacherNameList.forEach(item => {
        if (item != undefined) {
          teacherName = item;
        }
      })
      return teacherName;
    },
    //按次缺勤是否进入补课列表
    timeAsLeave() {
      if (!this.infoData) return false;
      let { attend_type, is_absenteeism } = this.infoData;
      return attend_type / 1 === 2 && is_absenteeism / 1 === 1;
    },
    isAfter() {
      if (!this.infoData) return true;
      let date = this.infoData.class_date;
      return (
        new Date(date).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0) >
        0
      );
    },
    className() {
      if (!this.infoData) return "";
      let infoData = this.infoData;
      return `${infoData.class_name} ${infoData.class_date}`;
    },
    attendanceText() {
      return this.allAttendance ? "取消考勤" : "一键考勤";
    },
    attendanceNum() {
      let attNum = 0;
      let countNum = 0;
      let rate = "0%";
      let { infoData } = this;
      let leave = 0;
      if (infoData) {
        attNum = infoData.attendance;
        countNum = infoData.count;
        rate = this.$calcPercent(infoData.attendance, infoData.count);
        leave = infoData.leave;
      }
      let str = `出勤情况: ${attNum} / ${countNum}  出勤率: ${rate}  请假人数:${leave}`;
      return str;
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.type = this.dialogType;
        this.shouldRefresh = false;
        this.classTime = this.items;
        let filter = this.$options.filters['filterTitle'];
        this.dialogTitle = filter(this.status);
        this.getList();
        this.getClassInfo();
        this.timetable_id = this.timetableId
      }
    }
  },
  filters: {
    filterTitle (status) {
      let arr = {'0':'点名', '1':'查看点名情况', '2':'操作'}
      return arr[status];
    },
    formatStatus (row, type) {
      console.log('%clogs','font-size:40px;color:pink;',row.is_duty)
      let value
      if(row.is_duty == '0'){
        value = '0'
      }else if(row.is_duty == '1'){
        value = '1'
      }else {
        value = '2'
      }
      if(!type){
        let arr = {'0':'缺勤', '1':'出勤', '2':'请假'}
        return arr[value]?arr[value]:'未知状态'
      }else{
        let typeArr = {'0':'danger', '1':'success', '2':'warning'}
        return typeArr[value]?typeArr[value]:''
      }
    }
  },
  created() {
    this.getList()
  }
};
</script>

<style lang="stylus" scoped>
.top-bar
  display: flex;
  margin-bottom: 10px;
  .label
    align-self: center;
    margin-right: 20px;
  .img-box
    flex: 1;
    text-align: right;
    line-height: 36px;
    font-size: 14px;
.header
  display flex
  .header-left
    flex 1
    .header-left-list
      margin-bottom 10px
      line-height 30px
      &:nth-child(1)
        i
          display inline-block
          margin-right 5px
          border-radius 50%
          width 30px
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
    .header-left-list-wrap
      display flex
      margin 20px 0
      .header-list-left
        flex 1
      .header-list-right
        flex 1
        text-align right
  .header-right
    flex 1
    text-align right
.edit-btn
  color #0084ff
  cursor pointer
</style>

