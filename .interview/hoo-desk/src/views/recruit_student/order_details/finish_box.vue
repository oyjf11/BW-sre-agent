<template>
  <el-dialog
    :title="finishType === 1 ?  '结课':'赠送'"
    class="end-course-dialog"
    @close="close"
    :visible.sync="dialogShow"
  >
    <div class="table-box">
      <table>
        <thead>
          <tr>
            <td>年级</td>
            <td>学期</td>
            <td>科目</td>
            <template v-if="finishType === 1">
              <td>剩余/总课时</td>
              <td>调整后课时</td>
              <td>报名时优惠</td>
              <td>调整后优惠</td>
              <td>教材费</td>
              <td>调整后应收</td>
              <td>操作</td>
            </template>
            <template v-else>
              <td>应收</td>
              <!-- <td>赠送课时</td> -->
              <td>优惠金额</td>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr
            :class="[item.status/ 1 === 2 ? 'disable':'']"
            v-for="(item,index) in courseList"
            :key="index"
          >
            <td class="disable">{{item.grade ? item.grade :"-"}}</td>
            <td class="disable">{{item.course_term ? item.course_term : "-"}}</td>
            <td class="disable">{{item.subject_name ? item.subject_name :"-"}}</td>
            <template v-if="finishType === 1">
              <td class="disable" style="width:110px">{{item.surplus_hours}} / {{courseDataList[index].courseTotalTime}}</td>
              <td>
                <template v-if="item.attend_type/ 1 === 1">
                  <el-button
                    type="text"
                    @click="openDateSelect(index)"
                  >{{item.select_day.length * item.hours}}</el-button>
                </template>
                <el-input-number
                  v-else
                  v-model="item.nowTimes"
                  :disable="item.status/1 === 2"
                  placeholder="请输入调整后课时"
                  @change="timeChange(index)"
                  :controls="false"
                  size="small"
                  :min="0"
                ></el-input-number>
              </td>
              <td class="disable">{{item.sub_reduce}}</td>
              <td>
                <el-input-number
                  v-model="item.nowReduces"
                  :disable="item.status/1 === 2"
                  placeholder="请输入调整后优惠"
                  @change="inputChange"
                  size="small"
                  :controls="false"
                  :min="0"
                ></el-input-number>
              </td>
              <td>
                <el-input-number
                  v-model="item.nowSundryFees"
                  placeholder="请输入教材费"
                  @change="inputChange"
                  :controls="false"
                  size="small"
                  :min="0"
                ></el-input-number>
              </td>
              <td class="disable">{{courseDataList[index].totalPrice}}</td>
              <td>
                <el-button type="text" @click="endItemZero(index)">全部结课</el-button>
              </td>
            </template>
            <template v-else>
              <td class="disable">{{item.sub_total}}</td>
              <!-- <td>
              <el-input placeholder="请输入赠送课时"></el-input>
              </td>-->
              <td>
                <el-input-number
                  v-model="item.inc_money"
                  :disable="item.status/1 === 2"
                  placeholder="请输入优惠金额"
                  :controls="false"
                  size="small"
                  :min="0"
                ></el-input-number>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="price-box" v-if="finishType === 1">
      <div class="label">结课金额</div>
      <div>{{refundCount}}</div>
    </div>
    <div class="textarea-box">
      <div class="label">{{finishType === 1?'结课原因':"赠送原因"}}:</div>
      <el-input type="textarea" placeholder="请输入原因" v-model="reason"></el-input>
    </div>
    <div slot="footer" class="dialog-btn-bar">
      <el-button @click="close">取消</el-button>
      <el-button type="primary" v-if="finishType === 1" @click="submit">确认</el-button>
      <el-button type="primary" v-else @click="addCourseSubmit">确认</el-button>
    </div>
  </el-dialog>
</template>


<script>
import { mapGetters } from "vuex";
import { reduceCourseTime, addCourseTime } from "@/api/course_control";
export default {
  props: {
    info: {},
    dialog: { type: Boolean, default: false },
    orderInfo: {},
    finishType: null
  },
  data() {
    return {
      courseInfo: null,
      dialogShow: false,
      courseList: [],
      dateSelectIndex: null,
      reason: ""
    };
  },
  methods: {
    timeChange(index) {
      let list = this.$copyObject(this.courseList);
      let item = list[index];
      let time = item.used_times / 1 + (item.nowTimes ? item.nowTimes : 0);
      item.nowReduces = (time * this.courseDataList[index].hourReduce).toFixed(2);
      this.courseList = list;
    },
    inputChange() {
      this.courseList = this.$copyObject(this.courseList);
    },
    endItemZero(index) {
      let list = this.$copyObject(this.courseList);
      let item = list[index];
      let courseData = this.courseDataList[index];
      let tiems;
      if (item.attend_type / 1 === 1) {
        item.select_day = [];
        tiems = courseData.beforeTime.length;
      } else {
        tiems = item.used_times ? item.used_times / 1 : 0;
        item.nowTimes = 0;
      }
      item.nowReduces = (tiems * courseData.hourReduce).toFixed(2);
      this.courseList = list;
    },
    submit() {
      if (!this.reason) {
        this.$message.error("请输入结课原因");
        return;
      }
      let tempList = this.$copyObject(this.courseList);
      tempList.forEach((item, index) => {
        if (item.attend_type / 1 === 1) {
          let beforeTime = this.courseDataList[index].beforeTime;
          let tempTime = [...beforeTime, ...item.select_day];
          item.time_table = tempTime;
          delete item.select_day;
          delete item.canSelectDay;
          item.times = tempTime.length;
        } else {
          item.times = ((item.nowTimes ? item.nowTimes : 0) + item.used_times / 1) / item.hours;
        }
        item.start_date = this.$getTimeStamp(item.start_date);
        item.end_date = this.$getTimeStamp(item.end_date);
        item.reduce = item.nowReduces;
        item.discount = 100;
        item.sundry_fees = item.nowSundryFees;
        delete item.nowSundryFees;
        delete item.nowTimes;
        delete item.nowReduces;
      });
      reduceCourseTime({
        course_list: JSON.stringify(tempList),
        order_id: this.$route.query.order_id,
        dec_reason: this.reason
      })
        .then(res => {
          this.$message.success("结课成功");
          this.close();
          this.$store.commit("setOrderDetailRefresh", true);
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    addCourseSubmit() {
      let tempList = this.$copyObject(this.courseList);
      tempList.forEach(item => {
        item.start_date = this.$getTimeStamp({ time: item.start_date });
        item.end_date = this.$getTimeStamp({ time: item.end_date });
      });
      addCourseTime({
        course_list: JSON.stringify(tempList),
        order_id: this.$route.query.order_id,
        inc_reason: this.reason
      })
        .then(res => {
          this.$message.success("赠送成功");
          this.close();
          this.$store.commit("setOrderDetailRefresh", true);
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    openDateSelect(index) {
      let item = this.courseList[index];
      let timeRange = [item.start_date, item.end_date];
      let date = item.select_day;
      let canSelectDay = item.canSelectDay;
      this.dateSelectIndex = index;
      this.$store.commit("setSelectData", {
        timeRange,
        date,
        canSelectDay,
        info: item
      });
      this.$store.commit("setDataSelectBrotherGet", true);
      this.$store.commit("setDateSelectShowBtn", true);
      this.$store.commit("setDateSelectShow", true);
    },
    toEndCourse() {
      if (!this.courseInfo.reason) {
        this.$message.error("请输入结课原因");
        return;
      }
      this.$confirm("确定结课吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          this.$emit("onChange", this.courseInfo);
        })
        .catch(() => {});
    },
    close() {
      this.dialogShow = false;
      this.reason = "";
      this.$emit("onClose", false);
    },
    getData() {
      this.courseList.forEach(item => {
        if (item.attend_type / 1 === 1) {
          item.select_day = this.$copyObject(item.modifiable_time_table);
          item.canSelectDay = this.$copyObject(item.modifiable_time_table);
        } else {
          item.nowTimes = item.surplus_hours;
        }
        item.nowReduces = item.sub_reduce;
        item.nowSundryFees = item.sundry_fees;
      });
    }
  },
  computed: {
    ...mapGetters(["dateSelectSubmitData"]),
    // 课程数据列表
    courseDataList() {
      let arr = this.courseList.map((item, index) => {
        let {
          price,
          hours,
          times,
          nowTimes = 0,
          nowReduces = 0,
          used_times = 0,
          select_day,
          modifiable_time_table,
          time_table,
          grade,
          sub_reduce,
          nowSundryFees = 0,
          course_term,
          subject_name
        } = item;
        // 课程金额计算
        let coursePrice = 0;
        let hourReduce = 0; // 每课时优惠金额
        let courseTotalTime = 0; // 报名时总课时
        let beforeTime;
        if (item.attend_type / 1 === 1) {
          let time1 = item.modifiable_time_table;
          let time2 = item.time_table;
          beforeTime = time2.filter(x => !time1.some(y => y === x));
          let tempTime = [...beforeTime, ...item.select_day];
          courseTotalTime = item.time_table.length * hours;
          coursePrice = tempTime.length * hours * price;
          if(courseTotalTime != 0 ) hourReduce = (sub_reduce / courseTotalTime) * hours;
        } else {
          courseTotalTime = times * hours;
          coursePrice = (nowTimes + used_times / 1) * price;
          if(courseTotalTime != 0) hourReduce = sub_reduce / courseTotalTime;
        }
        coursePrice = coursePrice - nowReduces;
        // 课程金额计算end
        let total = coursePrice + nowSundryFees / 1;
        if (total < 0) {
          this.$message.error(`${item.grade}${item.course_term}${item.subject_name}应收不能小于0`);
        }
        total = price < 0 ? 0 + nowSundryFees / 1 : total;
        total = total.toFixed(2);
        // 现应收end
        //退款金额列表
        let refund = item.sub_total - total;
        refund = refund < 0 ? 0 : refund;
        refund = refund.toFixed(2);
        //退款金额列表end
        return {
          courseTotalTime,
          refund,
          hourReduce,
          beforeTime,
          totalPrice: total,
          coursePrice
        };
      });
      return arr ? arr : [];
    },
    refundCount() {
      let num = 0;
      if (this.courseDataList.length != 0) {
        //退款金额小于0 变成 0
        let list = this.courseDataList.map((i, index) => i.refund);
        num = list.reduce((a, b) => {
          if (a < 0) a = 0;
          if (b < 0) b = 0;
          return a / 1 + b / 1;
        });
      }
      let wallet = num - this.orderInfo.diff_amount;
      num = (num / 1).toFixed(2);
      wallet = wallet < 0 ? 0 : wallet.toFixed(2);
      return `${num}元，其中退费到钱包余额${wallet}元`;
    }
  },
  watch: {
    dateSelectSubmitData(val) {
      let courseData = this.courseDataList[this.dateSelectIndex];
      let _length = courseData.beforeTime.length;
      _length = _length + val.length;
      this.courseList[this.dateSelectIndex].select_day = val;
      this.courseList[this.dateSelectIndex].nowReduces = (_length * courseData.hourReduce).toFixed(
        2
      );
      // 重置时间选择器，不然第二次打开，全部不可选。
      this.$store.commit("setSelectData", {
        timeRange: [],
        date: []
      });
    },
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.courseList = this.$copyObject(this.orderInfo.course_list);
        this.getData();
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.table-box
  overflow-x: auto;
table
  width: 100%;
  border: 1px solid #ebebeb;
  padding: 0 20px;
  tbody, thead
    tr
      td
        width: 80px;
        padding: 5px;
        border: 1px solid #ebebeb;
        text-align: center;
        vertical-align: middle;
        line-height: 18px;
        .el-input
          text-align: left;
  thead
    tr
      line-height: 40px;
  tbody
    tr
      td
        &.disable
          background: #f5f7fa;
      &.disable
        td
          background: #f5f7fa;
          color: #c0c4cc;
.price-box
  display: flex;
  margin-top: 20px;
  padding-right: 20px;
  font-size: 14px;
  .label
    flex: 0 0 auto;
    margin-right: 20px;
.textarea-box
  display: flex;
  margin-top: 20px;
  padding-right: 20px;
  .label
    font-size: 16px;
    flex: 0 0 auto;
    margin-right: 20px;
</style>
