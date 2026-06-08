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
              <td class="header-item">课程名称</td>
              <td class="header-item">班级</td>
              <td class="header-item">开始日期</td>
              <td class="header-item">结束日期</td>
              <!-- <td class="header-item">单次课时</td> -->
              <td class="header-item">课时单价</td>
              <td class="header-item">课时数</td>
              <td class="header-item">直减</td>
              <td class="header-item">折扣</td>
              <td class="header-item">教材费</td>
              <td class="header-item">应收</td>
              <td class="header-item">状态</td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item,index) in orderInfo.course_list" :key="index">
              <td>{{typeLabel[item.attend_type] ?typeLabel[item.attend_type] :"无" }}</td>
              <td class="can-click" @click="toChangeCourse(index, item.is_one_to_one)">{{item.course_name}}</td>
              <td
                class="can-click"
                @click="showClassFunc(item)"
              >{{item.class_name? item.class_name : "暂未排班"}}</td>
              <td
                v-if="item.attend_type / 1 ===1"
                :class="['time-item',statusList[index].selectDay ? '':'disabled']"
                colspan="2"
                @click="openSelect(index)"
              >{{item.select_day[0] ? item.select_day[0] :"未选择"}}</td>
              <template v-else>
                <td class="time-item">
                  <el-date-picker
                    v-model="item.start_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :clearable="item.attend_type / 1 === 2"
                    :disabled="statusList[index].start_date"
                    class="birthday"
                    placeholder="选择日期"
                    @change="timeChange(index)"
                    v-if="statusList[index].showStartTime"
                  ></el-date-picker>
                  <template v-else>-</template>
                </td>
                <td class="time-item">
                  <el-date-picker
                    v-model="item.end_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :disabled="statusList[index].end_date"
                    :clearable="item.attend_type / 1 === 2"
                    style="width:100%"
                    class="birthday"
                    placeholder="选择日期"
                    @change="timeChange(index)"
                    v-if="statusList[index].showEndTime"
                  ></el-date-picker>
                  <template v-else>-</template>
                </td>
              </template>
              <!-- <td class='input-td'>
                <el-input
                  type="text"
                  v-model="item.hours"
                  :disabled="statusList[index].hours"
                  placeholder="单次课时"
                  v-if="statusList[index].showHours"
                >
                  <template slot="append">时</template>
                </el-input>
                <template v-else>-</template>
              </td> -->
              <td class='input-td'>
                <el-input
                  type="text"
                  v-model="item.price"
                  :disabled="statusList[index].price"
                  placeholder="课时单价"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td class='input-td'>
                <template v-if="statusList[index].timesAlert">
                  <div class="times-box">
                    <div
                      :class="['time-num',statusList[index].times?'disabled':'']"
                      @click="openSelect(index)"
                    >{{item.times}}</div>
                    <div class="time-text">课时</div>
                  </div>
                </template>
                <template v-else-if="!statusList[index].showTimes">-</template>
                <el-input
                  type="text"
                  v-model="item.times"
                  :disabled="statusList[index].times"
                  placeholder="课程数量"
                  v-else
                >
                  <template slot="append">{{statusList[index].timesLabel}}</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input
                  type="text"
                  v-model="item.reduce"
                  :disabled="statusList[index].reduce"
                  placeholder="直减"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input
                  v-if="orderInfo && orderInfo.is_online_order / 1 === 0 "
                  type="text"
                  v-model="item.discount"
                  :disabled="statusList[index].discount"
                  placeholder="打折折扣 9折为90"
                >
                  <template slot="append">%</template>
                </el-input>
                <el-input
                  v-if="orderInfo && orderInfo.is_online_order / 1 === 1 "
                  type="text"
                  v-model="item.discount"
                  :disabled="statusList[index].discount"
                  :placeholder="(orderInfo.receivable_total / orderInfo.purchase_price*100).toFixed(2) "
                >
                  <template slot="append">%</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input
                  type="text"
                  v-model="item.sundry_fees"
                  :disabled="statusList[index].sundry_fees"
                >
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td>
                <p>{{total_price[index]}} 元</p>
              </td>
              <td style='width:80px;'>
                <el-button v-if="showDel[index]" v-show="orderInfo.course_list.length > 1" type="text" @click="delCourse(index)">删除</el-button>
                <template v-else>-</template>
              </td>
            </tr>
            <tr v-if="orderInfo.course_list.length == 0">
              <td style="height:40px" colspan="13">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="order-total-bar">
        共计:
        <!-- <span>{{orderInfo.receivable_total}}</span> 元 -->
        <span>{{orderTotal}}</span> 元
      </div>
      <div class="btn-bar">
        <!-- 已支付出现结课、赠送、换科按钮 -->
        <template v-if="payStatus&&endingClass">
          <el-button type="primary" :disabled="isEdit" @click="showEndCourse(1)">结课</el-button>
          <!-- <el-button type="primary" :disabled="isEdit" @click="showEndCourse(2)">赠送</el-button> -->
        </template>
        <el-button type="primary" v-if="courseBtnText" @click="toEdit">{{courseBtnText}}</el-button>
        <el-button @click="toCancle" v-if="courseBtnText == '保存'">取消</el-button>
        <el-span v-if="courseBtnText == '保存'">新增课程后请记得保存</el-span>
      </div>
    </div>
    <v-choose
      :attend_type="courseAttend_type"
      :dialog="showChoose"
      :oneToOne="is_one_to_one"
      @close="toClose"
      @chooseItem="addCourseItem"
    ></v-choose>
    <v-choose-class
      :courseInfo="bindCourseInfo"
      :dialog="showClassChoose"
      :oneToOne="is_one_to_one"
      @close="classChooseClose"
    ></v-choose-class>
    <v-finish
      :finishType="finishType"
      :orderInfo="orderInfo"
      :dialog="finishShow"
      @onClose="finishClose"
    ></v-finish>
    <v-date-select @onChange="selectDayChange"></v-date-select>
  </div>
</template>
<script>
import DateSelect from "../course_date_select/index";
import { AttrList } from "@/api/operations_center";
import chooseClass from "./choose_class";
import chooseCourse from "../choose_course";
import finishBox from "./finish_box";
export default {
  props: {
    info: {},
    payStatus: Boolean, // false 未支付 true 已支付
    discount_type: null, // 优惠计算规则 0：先减后折；1：先折后减；默认先减后折
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
      openItem: {
        info: null,
        index: "",
        showBtn: false
      },
      finishType: 1,
      selectDialog: false,
      typeLabel: this.$store.getters.getAttendTypeLabel,
      showClassChoose: false,
      bindCourseInfo: null, //传给选择班级组件的课程详情
      endingClass: false,
      changeIndex: null, // 换科的index
      courseAttend_type: "", // 选择课程组件的attend_type
      is_one_to_one: ""
    };
  },
  components: {
    "v-choose": chooseCourse,
    "v-finish": finishBox,
    "v-date-select": DateSelect,
    "v-choose-class": chooseClass
  },
  created() {
    this.getInfoData();
    this.getTerm();
    this.endingClass = this.$store.state.user.endClass;
  },
  methods: {
    //换科
    toChangeCourse(index, is_one_to_one) {
      if (this.addStatus) {
        this.$message.warning("请先完成新增订单");
        return;
      }
      let item = this.orderInfo.course_list[index];
      this.courseAttend_type = item.attend_type;
      this.changeIndex = index;
      this.is_one_to_one = is_one_to_one;
      this.showChoose = true;
      this.isEdit = true;
    },
    //排班
    showClassFunc(item, status) {
      if (this.isEdit) {
        this.$message.warning("请先完成编辑");
        return;
      } else if (this.addStatus) {
        this.$message.warning("请先完成新增订单");
        return;
      } else if (item.surplus_hours / 1 === 0) {
        this.$message.error("剩余课时为0不支持排入班级");
        return;
      }
      this.bindCourseInfo = item;
      this.is_one_to_one = item.is_one_to_one;
      console.log('%citem.is_one_to_one','font-size:40px;color:pink;',this.is_one_to_one)
      this.showClassChoose = true;
    },
    classChooseClose() {
      this.showClassChoose = false;
    },
    selectDayChange(day) {
      this.orderInfo.course_list[this.openItem.index].select_day = day;
      this.orderInfo.course_list[this.openItem.index].times = day.length;
    },
    openSelect(index) {
      let item = this.orderInfo.course_list[index];
      let timeRange = [item.start_date, item.end_date];
      let date = this.$copyObject(item.select_day);
      let canSelectDay = this.$copyObject(item.time_table);
      this.openItem.index = index;
      this.openItem.info = { timeRange, date, canSelectDay, info: item };
      this.$store.commit("setDateSelectShowBtn", item.isNew);
      this.$store.commit("setDateSelectShow", true);
      this.$store.commit("setSelectData", {
        timeRange,
        date,
        canSelectDay,
        info: item
      });
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
    showEndCourse(type) {
      if (this.courseBtnText === "保存") {
        this.$message.warning("请先保存或取消再结课");
        return;
      }
      this.finishShow = true;
      this.finishType = type;
    },
    finishClose() {
      this.finishShow = false;
    },
    delCourse(index) {
      this.orderInfo.course_list.splice(index, 1);
    },
    toEdit() {
      if (this.addStatus || this.isEdit) {
        let courseList = this.orderInfo.course_list;
        let status = true;
        for (let i = 0; i < courseList.length; i++) {
          let { attend_type, start_date, end_date, course_name } = courseList[
            i
          ];
          attend_type = attend_type / 1;
          let str = "";
          if (attend_type === 2) {
            if (start_date || end_date) {
              if (start_date && end_date) {
                if (start_date - end_date > 0) {
                  str = course_name + "的开始时间不能大于结束时间";
                }
              } else if (!start_date) {
                str = "请输入" + course_name + "的开始时间";
              } else if (!end_date) {
                str = "请输入" + course_name + "的结束时间";
              }
            }
          } else if (attend_type === 3) {
            if (start_date - end_date > 0) {
              str = course_name + "的开始时间不能大于结束时间";
            }
          }
          if (str !== "") {
            this.$message.error(str);
            status = false;
            break;
          }
        }
        if (status) {
          this.postData();
          this.isEdit = false;
        }
      } else {
        this.isEdit = true;
      }
    },
    toCancle() {
      this.isEdit = false;
      this.changeIndex = null;
      this.courseAttend_type = "";
      this.getInfoData();
    },
    addCourse() {
      if (this.isEdit) {
        let str = `请退出${this.payStatus ? "换科" : "编辑"}模式后，在添加课程`;
        this.$message.warning(str);
        return;
      }
      this.showChoose = true;
    },
    addCourseItem(data) {
      // 换科
      if (this.changeIndex !== null) {
        let item = this.orderInfo.course_list[this.changeIndex];
        item.grade = data.grade;
        item.subject_name = data.subject_name;
        item.course_name = data.course_name;
        item.course_term = data.course_term;
        item.is_one_to_one = data.is_one_to_one;
        this.orderInfo.course_list.splice(this.changeIndex, 1, item);
        this.changeIndex = null;
        return;
      }
      let obj = data;
      let attend_type = obj.attend_type / 1;
      let date = attend_type ? obj.time_table : [];
      let item = { isNew: true, select_day: this.$copyObject(date) };
      let start_date = obj.start_date / 1;
      let end_date = obj.end_date / 1;
      // 一次性收费 start_date、end_date 置空
      // 按次 start_date = 0 、end_date = 0 则置空
      if (attend_type === 0 || (attend_type === 2 && start_date === 0)) {
        obj.start_date = "";
        obj.end_date = "";
      } else {
        // 按月收费-长期有效 初始值为0，开始时间为今天,结束时间推算得出。
        if (start_date / 1 === 0) {
          start_date = new Date().setHours(0, 0, 0, 0);
          end_date = new Date(start_date);
          end_date = end_date.setMonth(end_date.getMonth() + obj.times / 1);
          obj.isLong = true;
        }
        obj.start_date = this.$getTimeStamp(start_date, 13);
        obj.end_date = this.$getTimeStamp(end_date, 13);
      }
      obj = Object.assign({}, obj, item);
      this.orderInfo.course_list.push(obj);
      if (obj.attend_type / 1 === 1) {
        this.openSelect(this.orderInfo.course_list.length - 1);
      }
    },
    // 选择课程关闭回调
    toClose() { 
      this.showChoose = false;
      this.courseAttend_type = "";
      this.changeIndex = null;
    },
    postData(list) {
      let postData = this.$copyObject(list ? list : this.orderInfo.course_list);
      postData.forEach(item => {
        let date = this.$copyObject(item.select_day ? item.select_day : []);
        item.start_date = this.$getTimeStamp(item.start_date);
        item.end_date = this.$getTimeStamp(item.end_date);
        item.time_table = date;
        delete item.select_day;
      });
      this.$emit("onSubmit", JSON.stringify(postData));
    },
    //处理课程数据
    getInfoData() {
      console.log('%cthis.info','font-size:40px;color:pink;',this.info)
      let orderInfo = this.$copyObject(this.info);
      if (!orderInfo) return;
      orderInfo.course_list.forEach(item => {
        item.old_subject_name = item.subject_name;
        let attend_type = item.attend_type / 1;
        if (attend_type === 0 || (attend_type / 1 === 2 && !item.start_date)) {
          item.start_date = "";
          item.end_date = "";
        } else {
          item.start_date = this.$getTimeStamp(item.start_date, 13);
          item.end_date = this.$getTimeStamp(item.end_date, 13);
          item.select_day =
            item.time_table.length !== 0
              ? this.$copyObject(item.time_table)
              : [];
        }
      });
      this.orderInfo = orderInfo;
    },
    timeChange(index) {
      let orderList = this.orderInfo.course_list;
      let item = orderList[index];
      let { attend_type, start_date, end_date } = item;
      attend_type = attend_type / 1;
      if (attend_type === 3) {
        if (start_date - end_date > 0) {
          this.$message.error("开始日期需要大于结束日期");
        } else {
          let diff = this.$getDateDiff(start_date, end_date);
          let month = diff[0] * 12 + diff[1];
          if (diff[2] >= 0) {
            month = month + 1;
          }
          orderList[index].times = month;
        }
      }
      this.orderInfo.course_list = orderList;
    }
  },
  computed: {
    // 是否显示删除按钮
    showDel() {
      if (this.addStatus) {
        return this.orderInfo.course_list.map(val =>
          val.isNew === true ? true : false
        );
      // } else if (this.orderInfo.course_list.length > 1) {
      //   return this.orderInfo.course_list.map(i => this.isEdit);
      } else {
        return this.orderInfo.course_list.map(i => this.isEdit);
      }
    },
    // 订单总金额
    orderTotal() {
      if (this.total_price.length == 0) return;
      let total = this.total_price.reduce((a, b) => a / 1 + b / 1);
      return (total / 1).toFixed(2);
    },
    // 课程应收列表
    total_price() {
        let total_list = this.orderInfo.course_list.map(item => {
        let { price, hours, times, sundry_fees, reduce, discount } = item;
        let total = 0;
        total = price * hours * times - reduce;
        /**2020-07-20 bugfix*/
        // total = total < 0 ? 0 : total;
        total = (total * discount) / 100 + sundry_fees / 1;
        let returnNum = this.$myFixed(total, 2)
        return returnNum
        // return total.toFixed(2);
      });
      return total_list;
    },
    // 状态列表
    statusList() {
      if (!this.orderInfo.course_list) return [];
      let list = this.orderInfo.course_list;
      let { payStatus, isEdit } = this;
      let arr = Array.from({ length: list.length });
      list.forEach((item, index) => {
        if (!arr[index]) arr[index] = {};
        let sta1; // 年级，学期，科目状态;
        let sta2; // 开始日期，结束日期，课时，单价，直减，折扣，教材费状态
        let selectDay = item.isNew ? true :false ; // 是否能开启时间选择组件
        let attend_type = item.attend_type / 1;
        if (item.isNew) {
          sta1 = false;
          sta2 = false;
        } else {
          sta1 = !isEdit || item.status == 2;
          sta2 = sta1 || payStatus;
        }
        let obj = {
          selectDay: selectDay,
          showTimeRange: false,
          showHours: false,
          showTimes: true,
          timesAlert: false,
          timesLabel: "课时",
          showStartTime: true,
          showEndTime: true
        };
        // 填充数据
        let _temp = ["grade", "term", "subject"];
        _temp.forEach(i => (obj[i] = sta1));
        _temp = ["start_date","end_date","hours","times","price","reduce","discount","sundry_fees"];
        _temp.forEach(i => (obj[i] = sta2));
        //end
        switch (attend_type) {
          case 1:
            obj.showTimeRange = true;
            obj.showHours = true;
            obj.timesAlert = true;
            break;
          case 3:
            obj.timesLabel = "月";
            obj.times = true;
            break;
          case 0:
            obj.showHours = true;
            obj.showStartTime = false;
            obj.showEndTime = false;
            break;
        }
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
        // 已支付显示换科
        return this.payStatus ? false : "编辑";
      }
    }
  },
  watch: {
    info() {
      this.getInfoData();
    }
  }
};
</script>

<style lang="stylus" scoped>
.times-box
  display: inline-table;
  text-align: center;
  height: 100%;
  min-height: 36px;
  line-height: 36px;
  .time-num
    display: table-cell;
    width: 100%;
    color: #03a9fe;
    font-size: 14px;
    cursor: pointer;
    &.disabled
      background-color: #f5f7fa;
      color: #c0c4cc;
  .time-text
    border-left: 1px solid #ebebeb;
    display: table-cell;
    padding: 0 5px;
    border-radius: 0;
    background-color: #f5f7fa;
    color: #909399;
.order-details-course-list
  padding: 0 20px;
.list-box
  box-sizing: border-box;
  margin-top: 20px;
  overflow-x: auto;
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
      vertical-align: middle;
      &.input-td
        width:110px;
      &.time-item
        .el-input
          width: 100%;
      &.select-item
        .el-input
          width: 100px;
      &.time-item
        color: #03a9fe;
        cursor: pointer;
        width: 116px;
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

el-span
  margin-left: 30px;
  color: 	#A9A9A9;
  font-size: 13px;
</style>
