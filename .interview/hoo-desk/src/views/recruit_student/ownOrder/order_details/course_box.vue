<template>
  <div class="order-details-course-list">
    <div class="order-box">
      <div class="tips-bar">2.选择课程
        <el-button
          v-if="orderInfo && orderInfo.is_online_order / 1 === 0 "
          style="margin-left:10px"
          size="mini"
          @click="addCourse"
        >新增课程</el-button>
      </div>
      <div class="list-box">
        <table class="list">
          <thead class="list-header">
            <tr>
              <td class="header-item">类别</td>
              <td class="header-item">年级</td>
              <td class="header-item">学期</td>
              <td class="header-item">科目</td>
              <td class="header-item">开始日期</td>
              <td class="header-item">结束日期</td>
              <td class="header-item">单次课时</td>
              <td class="header-item">课时单价</td>
              <td class="header-item">课程次数</td>
              <td class="header-item">直减</td>
              <td class="header-item">折扣</td>
              <td class="header-item">教材费</td>
              <td class="header-item">应收</td>
              <td class="header-item">操作</td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item,index) in orderInfo.course_list" :key="index">
              <td>{{typeLabel[item.attend_type] ?typeLabel[item.attend_type] :"无" }}</td>
              <td class="select-item" style="width:200px;">
                <el-select
                  style="width:100%"
                  v-model="item.grade"
                  :disabled="statusList[index].grade"
                >
                  <el-option
                    v-for="option in gradeList"
                    :key="option.attr_id"
                    :label="option.attr_value"
                    :value="option.attr_value"
                  ></el-option>
                </el-select>
              </td>
              <td class="select-item" style="width:200px;">
                <el-select
                  style="width:100%"
                  v-model="item.course_term"
                  :disabled="statusList[index].term"
                >
                  <el-option
                    v-for="option in termList"
                    :key="option.attr_id"
                    :label="option.attr_value"
                    :value="option.attr_value"
                  ></el-option>
                </el-select>
              </td>
              <td class="select-item">
                <el-select v-model="item.subject_name" :disabled="statusList[index].subject">
                  <el-option
                    v-for="option in subjectList"
                    :key="option.attr_id"
                    :label="option.attr_value"
                    :value="option.attr_value"
                  ></el-option>
                </el-select>
              </td>
              <template v-if="item.attend_type / 1 ===1">
                <td
                  :class="['time-item','time-item-large',statusList[index].selectDay ? 'disabled':'']"
                  colspan="2"
                  @click="openSelect(index)"
                >{{item.select_day[0] ? item.select_day[0] :"未选择"}}</td>
              </template>
              <template v-else>
                <td class="time-item">
                  <el-date-picker
                    v-model="item.start_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :clearable="false"
                    :disabled="statusList[index].start_date"
                    class="birthday"
                    placeholder="选择日期"
                  ></el-date-picker>
                </td>
                <td class="time-item">
                  <el-date-picker
                    v-model="item.end_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :disabled="statusList[index].end_date"
                    :clearable="false"
                    style="width:100%"
                    class="birthday"
                    placeholder="选择日期"
                  ></el-date-picker>
                </td>
              </template>

              <td>
                <el-input
                  type="text"
                  class="price"
                  v-model="item.hours"
                  :disabled="statusList[index].hours"
                  placeholder="单次课时"
                >
                  <template slot="append">时</template>
                </el-input>
              </td>
              <td>
                <el-input
                  type="text"
                  class="price"
                  v-model="item.price"
                  :disabled="statusList[index].price"
                  placeholder="课时单价"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td>
                <el-input
                  type="text"
                  class="price"
                  v-model="item.times"
                  :disabled="statusList[index].times"
                  placeholder="课程数量"
                >
                  <template slot="append">次</template>
                </el-input>
                
              </td>
              <td>
                <el-input
                  type="text"
                  v-model="item.reduce"
                  class="name"
                  :disabled="statusList[index].reduce"
                  placeholder="直减"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td>
                <el-input
                  v-if="orderInfo && orderInfo.is_online_order / 1 === 0 "
                  type="text"
                  v-model="item.discount"
                  class="name"
                  :disabled="statusList[index].discount"
                  placeholder="打折折扣 9折为90"
                >
                  <template slot="append">%</template>
                </el-input>
                <el-input
                  v-if="orderInfo && orderInfo.is_online_order / 1 === 1 "
                  type="text"
                  v-model="item.discount"
                  class="name"
                  :disabled="statusList[index].discount"
                  :placeholder="(orderInfo.receivable_total / orderInfo.purchase_price*100).toFixed(2) "
                >
                  <template slot="append">%</template>
                </el-input>
              </td>
              <td>
                <el-input
                  type="text"
                  v-model="item.sundry_fees"
                  :disabled="statusList[index].sundry_fees"
                  class="name"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td>
                <p>{{item.sub_total}} 元</p>
              </td>
              <td>
                <el-button v-if="!item.isNew" type="text" @click="showEndCourse(item,index)">结课</el-button>
                <el-button v-else type="text" @click="delCourse(index)">删除</el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="order-total-bar">
        共计:
        <span>{{orderTotal}}</span> 元
      </div>
      <div class="btn-bar">
        <el-button v-if="orderInfo" type="primary" @click="toEdit">{{courseBtnText}}</el-button>
        <el-button @click="toCancle" v-if="courseBtnText != '编辑'">取消</el-button>
      </div>
    </div>
    <v-choose v-if="showChoose" @close="toClose" @chooseItem="addCourseItem"></v-choose>
    <v-finish
      @onChange="finishSubmit"
      :orderInfo="orderInfo"
      :dialog="finishShow"
      :info="finishInfo"
      @onClose="finishClose"
    ></v-finish>
    <v-date-select
      @onChange="selectDayChange"
      @onClose="selectClose"
      :dialog="selectDialog"
      :showBtn='openItem.showBtn'
      :info="openItem.info"
    ></v-date-select>
  </div>
</template>
<script>
import DateSelect from "../course_date_select/index";

import { AttrList } from "@/api/operations_center";
import chooseCourse from "@/views/recruit_student/choose_course";
import finishBox from "./finish_box";
export default {
  props: {
    info: {},
    payStatus: {}
  },
  data() {
    return {
      isEdit: false, //是否编辑
      gradeList: [],
      termList: [],
      subjectList: [],
      showChoose: false,
      orderInfo: null,
      finishShow: false,
      finishInfo: null,
      finishIndex: 0,
      isFinish: false,
      openItem: {
        info: null,
        index: "",
        showBtn:false
      },
      selectDialog: false,
      typeLabel: this.$store.getters.getAttendTypeLabel
    };
  },
  components: {
    "v-choose": chooseCourse,
    "v-finish": finishBox,
    "v-date-select": DateSelect
  },
  created() {
    this.getInfoData();
    this.getTerm();
  },
  methods: {
    selectClose() {
      this.selectDialog = false;
    },
    selectDayChange(day) {
      this.orderInfo.course_list[this.openItem.index].select_day = day;
      // this.orderInfo.course_list[this.openItem.index].times = day.length;
    },
    openSelect(index) {
      this.openItem.showBtn = !this.statusList[index].selectDay
      let { course_list } = this.orderInfo;
      let item = course_list[index];
      this.openItem.index = index;
      let timeRange = [item.start_date, item.end_date];
      let date = this.$copyObject(item.select_day);
      let canSelectDay = this.$copyObject(item.time_table);
      console.log("date",date,canSelectDay,item.select_day,item.time_table)
      this.openItem.info = { timeRange, date, canSelectDay, info: item };
      
      this.selectDialog = true;
    },
    getTerm() {
      AttrList()
        .then(res => {
          this.termList = res.data.term;
          this.subjectList = res.data.subject;
          this.gradeList = res.data.grade;
        })
        .catch(e => {
          console.log(e);
        });
    },
    showEndCourse(item, index) {
      if (this.courseBtnText === "保存") {
        this.$message.warning("请先保存或取消再结课");
        return;
      }
      this.finishShow = true;
      this.finishInfo = item;
      this.finishIndex = index;
    },
    finishSubmit(val) {
      let list = this.$copyObject(this.orderInfo.course_list);
      list[this.finishIndex] = val;
      this.postData(list);
    },
    delCourse(index) {
      this.orderInfo.course_list.splice(index, 1);
    },
    finishClose() {
      this.finishShow = false;
    },
    toEdit() {
      if (this.addStatus || this.isEdit) {
        this.isEdit = false;
        this.postData();
      } else {
        this.isEdit = true;
      }
    },
    toCancle() {
      this.isEdit = false;
      this.getInfoData();
    },
    addCourse() {
      if (this.isEdit) {
        this.$message.warning("请退出编辑模式后，再添加课程");
        return;
      }
      this.showChoose = true;
    },
    addCourseItem(data) {
      // this.showOrderInfo = true;
      let obj = data;
      let date =  obj.time_table;
      let item = { isNew: true, select_day: this.$copyObject(date) };
      obj.start_date = this.$getTimeStamp({time:obj.start_date ?obj.start_date : new Date(),length:13});
      obj.end_date = this.$getTimeStamp({time:obj.end_date ? obj.end_date :new Date(),length:13});
      obj = Object.assign({}, obj, item);
      this.orderInfo.course_list.push(obj);
      if(obj.attend_type / 1 === 1){
        this.openSelect(this.orderInfo.course_list.length - 1)
      }
    },
    toClose() {
      this.showChoose = false;
    },
    postData(list) {
      let postData = this.$copyObject(list ? list : this.orderInfo.course_list);
      postData.forEach(item => {
        let date = this.$copyObject(item.select_day);
        item.start_date = this.$getTimeStamp({time:item.start_date});
        item.end_date = this.$getTimeStamp({time:item.end_date});
        item.time_table = date;
        delete item.select_day;
      });
      this.$emit("onSubmit", JSON.stringify(postData));
    },
    getInfoData() {
      let orderInfo = this.$copyObject(this.info);
      if (!orderInfo) {
        return;
      }
      orderInfo.course_list.forEach(item => {
        item.start_date = this.$getTimeStamp({time:item.start_date,length:13});
        item.end_date = this.$getTimeStamp({time:item.end_date,length:13});
        item.select_day = this.$copyObject(item.time_table);
      });
      this.orderInfo = orderInfo;
    }
  },
  computed: {
    orderTotal() {
      let num = 0;
      if (
        this.orderInfo.course_list &&
        this.orderInfo.course_list.length != 0
      ) {
        this.orderInfo.course_list.forEach(
          item => (num = num + Number(item.sub_total))
        );
      }
      return num;
    },
    statusList() {
      if (!this.orderInfo.course_list) {
        return [];
      }
      let list = this.orderInfo.course_list;
      let { payStatus, isEdit } = this;
      let arr = Array.from({ length: list.length });
      list.forEach((item, index) => {
        if (!arr[index]) arr[index] = {};
        let sta1; // 年级，学期，科目状态;
        let sta2; // 开始日期，结束日期，课时，单价，直减，折扣，教材费状态
        let selectDay; // 是否能开启时间选择组件
        if (item.isNew) {
          sta1 = false;
          sta2 = false;
        } else {
          sta1 = !isEdit || item.status == 2;
          sta2 = sta1 || payStatus;
          selectDay = sta2 && !item.class_id;
        }
        let obj = {
          grade: false,
          term: false,
          subject: false,
          start_date: false,
          end_date: false,
          hours: false,
          times: false,
          price: false,
          reduce: false,
          discount: false,
          discount: false,
          sundry_fees: false,
          selectDay: false
        };
        arr[index] = obj;
      });
      return arr;
    },
    addStatus() {
      let status = false;
      if (this.orderInfo.course_list) {
        status = this.orderInfo.course_list.some(val => val.isNew === true);
      }
      return status;
    },
    courseBtnText() {
      if (this.addStatus || this.isEdit) {
        return "保存";
      } else {
        return "编辑";
      }
    }
  },
  watch: {
    info() {
      this.isFinish = false;
      this.getInfoData();
    }
  }
};
</script>

<style lang="stylus" scoped>
.times-box
  display:inline-table;
  text-align:center;
  height 100%;
  min-height:36px;
  line-height:36px;
  .time-num
    display:table-cell;
    width:100%;
    color:#03a9fe;
    font-size:14px;
    cursor:pointer;
    &.disabled
      background-color:#f5f7fa
      color:#c0c4cc;
  .time-text
    border-left: 1px solid #ebebeb;
    display:table-cell;
    padding: 0 5px;
    border-radius: 0;
    background-color: #f5f7fa;
    color: #909399;
.order-details-course-list
  padding: 0 20px;
.list-box
  box-sizing: border-box;
  margin-top: 20px;
.list
  width: 100%;
  border: 1px solid #ebebeb;
.list-header
  width: 100%;
  tr
    width: 100%;
  .header-item
    border: 1px solid #ebebeb;
    height: 40px;
    text-align: center;
    border-collapse: collapse;
    vertical-align: middle;
tbody
  tr
    td
      min-width: 80px;
      border: 1px solid #ebebeb;
      text-align: center;
      &.time-item, &.select-item
        .el-input
          width: 100px;
      &.time-item
        color: #03a9fe;
        cursor: pointer;
        &.time-item-large
          width: 200px;
        &.disabled
          background-color: #f5f7fa;
          color: #c0c4cc;
.order-total-bar
  text-align: right;
  margin: 10px 20px;
  span
    color: rgb(238, 26, 45);
.btn-bar
  margin-bottom: 20px;
  margin-left: 23px;
</style>
