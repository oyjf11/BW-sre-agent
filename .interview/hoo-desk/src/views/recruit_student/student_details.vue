<!--
 * @Author: 陈声钰
 * @Date: 2019-11-07 22:57:31
 * @LastEditors: 陈声钰
 * @LastEditTime: 2019-11-14 15:34:21
 * @Description: 学员详情
 * @FilePath: /new_hoo_desk/src/views/recruit_student/student_details.vue
 * @扑街
 -->
<template>
  <div class="index-wrap">
    <div class="header border">
      <el-row>
        <el-col :span="2" class="student-avatar">
          <el-avatar :size="80" :src="stu_detail_info.headimage"></el-avatar>
        </el-col>
        <el-col :span="18">
          <div class="student-name">
            <span>{{stu_detail_info.student_name}}</span>
            <i
              class="hoo"
              v-if="stu_detail_info.student_sex!=='u'"
              :class="['hoo',stu_detail_info.student_sex =='m' ? 'hoo-man' :'hoo-woman']"
            ></i>
          </div>
          <div class="gray">报名日期:{{stu_detail_info.join_date}}</div>
          <el-row>
            <el-col :span="8">
              <div>
                <span class="gray">联系电话:</span>
                <span>{{contacts_num}} ({{contacts_name}})</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div>
                <span class="gray">在读学校:</span>
                <span>{{stu_detail_info.school == '' ? '未填写' : stu_detail_info.school}}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div>
                <span class="gray">邮箱:</span>
                <span>{{stu_detail_info.email == '' ? '未填写' : stu_detail_info.email}}</span>
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="8">
              <div>
                <span class="gray">年级:</span>
                <span>{{stu_detail_info.grade == '' ? '未填写' : stu_detail_info.grade}}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div>
                <span class="gray">学员 QQ:</span>
                <span>{{stu_detail_info.qq_num == '' ? '未填写' : stu_detail_info.qq_num}}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div>
                <span class="gray">住址:</span>
                <span>{{stu_detail_info.address == '' ? '未填写' : stu_detail_info.address }}</span>
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="8">
              <div>
                <span class="gray">生日:</span>
                <span>{{stu_detail_info.birthday == '' ? '未填写' : stu_detail_info.birthday}}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div>
                <span class="gray">报名渠道:</span>
                <span>{{stu_detail_info.from == '' ? '未填写' : stu_detail_info.from}}</span>
              </div>
            </el-col>
          </el-row>
        </el-col>
        <el-col :span="4" style="text-align: right;">
          <el-button type="primary" @click="handleEdit">编辑学员</el-button>
        </el-col>
      </el-row>
    </div>
    <div class="content">
      <el-tabs class="pane-wrap" v-model="activeName">
        <el-tab-pane
          :label="item.text"
          :id="item.id"
          :name="item.name"
          v-for="(item,index) in tagsArr"
          :key="index"
        >
          <div :class="activeName!='registration'?'components-wrap':''">
            <component
              :is="item.component"
              :total="item.total"
              :ref="item.ref"
              :student_id="student_id"
              :tableList="item.listdata"
              :selectList="selectList"
              :selectTypeList="selectTypeList"
              :stuName="stuName"
              :search="search"
              @changeTab="filterTab"
              @datetime="filterChange($event,'datetime')"
              @search="filterChange($event,'search')"
              @pageChange="filterChange($event, 'page')"
              @sizeChange="filterChange($event,'size')"
              @onchange="OnChange"
            ></component>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <v-student
      :showStu="showStu"
      @handleOK="handleOK"
      @handleCancel="toCloseCreat"
      :edit-data="rowData"
    ></v-student>
  </div>
</template>

<script>
import studentModal from "./studentModal.vue";
import registration from "./student_details_record/registration_record";
import classRecord from "./student_details_record/classRecord_record";
import growthFile from "./student_details_record/growthFile_record";
// import attendClass from "./components/attendClass";
import {
  getStuDetails,
  getStuApplyList,
  getStuAttendList,
  getStuGrownList,
  // getClassListByCrmStuId,
  // courseRecordList,
  getAttendListByCrm
} from "@/api/student_control";

export default {
  data() {
    return {
      showStu: false, //编辑学员弹框
      rowData: {}, //编辑学生的数据对象
      tagsArr: [
        // {
        //   id: 0,
        //   text: "就读班级",
        //   value: 0,
        //   ref: "attendClass",
        //   name: "attendClass",
        //   component: "attend-class",
        //   listData: [],
        //   total: 0
        // },
        {
          id: 0,
          text: "报名记录",
          value: 0,
          ref: "registration",
          name: "registration",
          component: "v-registration",
          listdata: [],
          total: 0
        },
        {
          id: 1,
          text: "上课记录",
          value: 1,
          ref: "classRecord",
          name: "classRecord",
          component: "v-classRecord",
          listdata: [],
          total: 0
        },
        {
          id: 2,
          text: "成长档案",
          value: 2,
          ref: "growthFile",
          name: "growthFile",
          component: "v-growthFile",
          listdata: [],
          total: 0
        }
      ], //学员信息分类组件
      activeName: "registration",
      selectList: [],
      selectTypeList: [
        { comment_type: 1, label: "学习点评" },
        { comment_type: 7, label: "学员作业" }
      ],
      stu_detail_info: {
        student_name: "",
        headimage: "",
        student_sex: "",
        contacts: [],
        school: "",
        email: "",
        grade: "",
        qq_num: "",
        address: "",
        birthday: "",
        from: "",
        join_date: ""
      }, //学员详细信息
      stuName: "",
      student_id: "", //学员ID
      org_id: "", //机构ID
      contacts_num: "", //联系人号码
      contacts_name: "", //联系人称谓，爸爸、妈妈...
      page: 1, //列表数据默认显示第一页
      size: 10, //列表数据默认一页10条数据
      comment_type: "",
      tableLoading: false,
      count: 1, //数据总条数
      search: "", //搜索字段
      datetime: "",
      recordDatetime: "",
      growthDatetime: "",
      class_id: "",
      transDate: []
    };
  },
  components: {
    "v-registration": registration,
    "v-classRecord": classRecord,
    "v-growthFile": growthFile,
    "v-student": studentModal,
    // attendClass
  },
  methods: {
    /**
     * 获取当前时间与上一个月的时间，默认显示最近一个月的数据
     */
    getInitTime() {
      let dateArr = [];
      let myDate = new Date();
      myDate.setDate(myDate.getDate() - 30);
      let dateTemp; // 临时日期数据
      let flag = 1;
      for (let i = 0; i < 31; i++) {
        dateTemp =
          myDate.getFullYear() +
          "-" +
          (myDate.getMonth() + 1) +
          "-" +
          myDate.getDate();
        dateArr.push(dateTemp);
        myDate.setDate(myDate.getDate() + flag);
      }
      this.transDate = [dateArr[0], dateArr[dateArr.length - 1]];
      let s = new Date(dateArr[0]);
      let e = new Date(dateArr[dateArr.length - 1]);
      this.datetime = [s.getTime() / 1000, e.getTime() / 1000];
    },

    /**
     * 初始化获取信息
     */
    getInfoList() {
      this.getStudentApplyList();
      this.getStudentAttendList();
      this.getStudentGrownList();
      // this.getClassListByCrmStuId();
    },

    /**
     * 获取子组件的搜索字段
     */
    OnChange(obj) {
      if (obj.id == 1) {
        this.recordDatetime = obj.val.datetime;
        this.search = obj.val.search;
        this.getStudentAttendList('search');
      } else if (obj.id == 2) {
        this.growthDatetime = obj.val.datetime;
        this.class_id = obj.val.class_id;
        this.comment_type = obj.val.comment_type;
        this.getStudentGrownList();
      }
    },

    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val[0];
      if (val[1] == 2) {
        this.getStudentGrownList();//成长档案
      } else if (val[1] == 1) {
        this.getStudentAttendList('size');//上课记录
      } else {
        this.getStudentApplyList();//报名记录
      }
    },
    /**
     * 选项切换
     * Created by 陈声钰 on 2019/11/14 11:21:40
     */
    filterTab(val) {
      console.log("%c选项切换", "font-size:40px;color:pink;", val);
      this.activeName = this.tagsArr[val.index].name;
      this.search = val.search;
      // this.getStudentApplyList();
    },
    /**
     * 获取学员个人详细信息
     */
    getStudentDetails() {
      let obj = {
        student_id: this.student_id
      };
      getStuDetails(obj)
        .then(res => {
          this.stu_detail_info = res.data;
          this.stuName = res.data.student_name;
          this.contacts_num = this.stu_detail_info.contacts[0].phone;
          this.contacts_name = this.stu_detail_info.contacts[0].name;
          if (
            this.stu_detail_info.join_date == "" ||
            this.stu_detail_info.join_date == null ||
            this.stu_detail_info.join_date == undefined
          ) {
            return (this.stu_detail_info.join_date = "未填写");
          } else {
            return (this.stu_detail_info.join_date = this.$getSimpleDate(
              this.stu_detail_info.join_date
            ));
          }
        })
        .catch(error => {
          this.tableLoading = false;
          this.$message.error(error);
        });
    },

    /**
       * 获取学员报名记录列表
       */
      getStudentApplyList() {
        let obj = {
          student_id: this.student_id,
          org_id: this.org_id,
          page: this.page,
          count: this.size
        };
        this.tableLoading = true;
        getStuApplyList(obj)
            .then(res => {
              this.count = res.data.count;
              let list = res.data.list;
              list.forEach(item => {
                item.start_date = item.start_date != '' && item.start_date != null ? this.$formatToDate(item.start_date, 'Y-M-D') : '';
              })
              this.tagsArr[0].listdata = list;
              this.tagsArr[0].total = Number(res.data.count);
              this.tableLoading = false;
            })
            .catch(error => {
              this.tableLoading = false;
            })
      },

    /**
       * 获取学员上课记录列表
       */
      getStudentAttendList(type) {
        let obj = {}
        if (this.recordDatetime == '') { // 时间未选中时加载获取数据
          if (type == 'search'){ // 搜索时获取数据
            obj = {
              student_id: this.student_id,
              page: 1,
              count: 10,
              org_id: this.org_id,
              search: this.search,
            };
          } else { // 分页操作时获取数据
             obj = {
              student_id: this.student_id,
              page: this.page,
              count: this.size,
              org_id: this.org_id,
              search: this.search,
            };
          }
        } else { // 操作时
          if (type == 'search'){ // 搜索时获取数据
            obj = {
              student_id: this.student_id,
              page: 1,
              count: 10,
              org_id: this.org_id,
              search: this.search,
              start_time: this.recordDatetime[0],
              end_time: this.recordDatetime[1]
            };
          } else { // 分页操作时获取数据
             obj = {
              student_id: this.student_id,
              page: this.page,
              count: this.size,
              org_id: this.org_id,
              search: this.search,
              start_time: this.recordDatetime[0],
              end_time: this.recordDatetime[1]
            };
          }
        }
        this.tableLoading = true;
        getStuAttendList(obj)
            .then(res => {
              let list = res.data.list
              list.forEach(item => {
                if (item.teacher_name == '' || item.teacher_name == null) { // 判断如果teacher_name授课老师为空 取default_teacher填充
                  item.teacher_name = item.default_teacher
                }
              })
              this.tagsArr[1].listdata = list;
              this.tagsArr[1].total = Number(res.data.count);
              this.tableLoading = false;
            })
            .catch(error => {
              this.tableLoading = false;
            })
      },

      /**
       * 获取学员成长档案列表
       */
      getStudentGrownList() {
        let obj = {};
        if (this.growthDatetime == '') {
          obj = {
            student_id: this.student_id,
            page: this.page,
            count: this.size,
            class_id: this.class_id,
            comment_type: this.comment_type// 默认显示图文，目前只有一种情况
          };
        } else {
          obj = {
            student_id: this.student_id,
            page: this.page,
            count: this.size,
            class_id: this.class_id,
            start_time: this.growthDatetime[0],
            end_time: this.growthDatetime[1],
            comment_type: this.comment_type// 默认显示图文，目前只有一种情况
          };
        }
        this.tableLoading = true;
        getStuGrownList(obj)
            .then(res => {
              let list = res.data.list;
              list.forEach(item => {
                item.video.forEach( i => {
                  i.isPlay = false;
                })
              })
              this.tagsArr[2].listdata = list;
              console.log('%clist','font-size:40px;color:pink;',list)
              this.tagsArr[2].total = Number(res.data.total);
              this.selectList = res.data.class_list;
              this.tableLoading = false;
            })
            .catch(error => {
              this.tableLoading = false;
            })
      },
    /**
     * 点击编辑学员信息
     */
    handleEdit() {
      this.rowData = this.stu_detail_info;
      this.showStu = true;
    },

    /**
     * 关闭新建学员窗口
     */
    toCloseCreat() {
      this.rowData = {};
      this.showStu = false;
    },

    /**
     * 创建或编辑成功的回调
     * @param message
     */
    handleOK(message) {
      this.getStudentDetails();
      this.showStu = false;
      this.$message.success(message);
    }
  },
  created() {
    this.student_id = this.$route.query.student_id;
    this.org_id = this.$route.query.org_id;
    this.getInitTime();
    this.getStudentDetails();
    this.getInfoList();
  },
  mounted() {
    if (this.$route.query.index) {
      this.activeName = this.tagsArr[this.$route.query.index].name;
    }
    if (this.$route.query.search) {
      this.search = this.$route.query.search;
    }
  }
};
</script>

<style lang="stylus" scoped>
.header {
  padding: 30px;
  color: $black;

  .student-avatar {
    text-align: center;
  }

  .student-name {
    font-size: 20px;
    line-height: 36px;

    .hoo-woman {
      font-size: 17px;
      color: #fd908c;
    }

    .hoo-man {
      font-size: 17px;
      color: #57a3fc;
    }
  }

  .gray {
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 20px;
    color: $gray;
  }
}

.border {
  border-bottom: 10px solid #f6f8fb;
}

.index-wrap >>> .el-tabs__nav-wrap {
  padding-left: 30px;

  .el-tabs__item {
    height: 60px;
    line-height: 60px;
  }
}

.components-wrap {
  padding: 10px 20px;
}
</style>
