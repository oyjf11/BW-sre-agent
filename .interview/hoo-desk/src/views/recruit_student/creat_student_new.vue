<template>
  <div class="create-new-student" v-loading.fullscreen.lock="fullscreenLoading">
    <div class="student-info-wrap">
      <div class="tips-bar">1.学生信息</div>
      <div class="student-info">
        <el-row type="flex" class="header-bar">
          <el-col style="flex:0 0 220px">学生姓名</el-col>
          <el-col>联系人称呼</el-col>
          <el-col>电话号码</el-col>
          <el-col>备注</el-col>
        </el-row>
        <el-row type="flex" class="input-bar">
          <el-col style="flex:0 0 220px">
            <el-autocomplete
              class="student-list-search"
              v-model="studentName"
              placement="bottom-end"
              :debounce="500"
              :fetch-suggestions="searchStudent"
              placeholder="请输入姓名或手机号码"
              popper-class="create-student-list"
              @select="handleSelect"
              :disabled="showButton"
            >
              <template slot-scope="{ item }">
                <p class="info">{{ item.student_name }} - {{ item.contacts[0].phone }}</p>
              </template>
            </el-autocomplete>
          </el-col>
          <el-col>
            <el-input
              type="text"
              v-model="stuInfo.contacts[0].name"
              class="name"
              :disabled="showButton"
            ></el-input>
          </el-col>
          <el-col>
            <el-input
              type="text"
              v-model="stuInfo.contacts[0].phone"
              class="name"
              :disabled="showButton"
            ></el-input>
          </el-col>
          <el-col>
            <el-input
              type="text"
              v-model="stuInfo.contacts[0].remark"
              class="remark"
              :disabled="showButton"
            ></el-input>
          </el-col>
        </el-row>
        <el-row type="flex" class="btn-bar">
          <el-col :span="3">
            <el-button type="primary" @click="toCreatStu" :disabled="showButton">确认</el-button>
          </el-col>
          <el-col :span="3" :offset="1">
            <el-button @click="reset">重置</el-button>
          </el-col>
        </el-row>
      </div>
    </div>
    <div class="order-wrap" v-if="student_id">
      <div class="order-box">
        <div class="tips-bar">2.选择课程</div>
        <el-button class="creat_bt—b create-btn" @click="toChoose">
          <i class="fa fa-plus" style="color: #7B9ED4;"></i>&ensp;添加课程
        </el-button>
        <table class="list" v-if="orderList.length !=0">
          <thead class="list-header">
            <tr>
              <td>类别</td>
              <td>课程名称</td>
              <td>开始日期</td>
              <td>结束日期</td>
              <td>单次课时</td>
              <td>课时单价</td>
              <td>课时数</td>
              <td>直减</td>
              <td>折扣</td>
              <td>教材费</td>
              <td>应收</td>
              <td>操作</td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item,index) in orderList" :key="index">
              <td>{{typeLabel[item.attend_type]}}</td>
              <td>{{item.course_name}}</td>
              <!-- 开始时间 - 结束时间 -->
              <!-- 按期的点击使用选择日期上课组件，其他使用普通组件 -->
              <td
                v-if="statusList[index].showTimeRange"
                class="time-item time-item-large"
                colspan="2"
                @click="openSelect(index)"
              >{{item.select_day[0] ? item.select_day[0] :"未选择"}}</td>
              <template v-else>
                <td class="time-item">
                  <el-date-picker
                    v-if="statusList[index].showStartTime"
                    v-model="item.start_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :clearable="item.attend_type / 1 === 2"
                    class="birthday"
                    style="width:100%"
                    placeholder="选择日期"
                    @change="timeChange(index)"
                  ></el-date-picker>
                  <template v-else>-</template>
                </td>
                <td class="time-item">
                  <el-date-picker
                    v-if="statusList[index].showEndTime"
                    v-model="item.end_date"
                    value-format="timestamp"
                    prefix-icon="null"
                    type="date"
                    :clearable="item.attend_type / 1 === 2"
                    style="width:100%"
                    class="birthday"
                    placeholder="选择日期"
                    @change="timeChange(index)"
                  ></el-date-picker>
                  <template v-else>-</template>
                </td>
              </template>
              <!-- 开始时间 - 结束时间 -->
              <td class='input-td'>
                <el-input
                  v-if="statusList[index].showHours"
                  type="text"
                  class="price"
                  v-model="item.hours"
                  placeholder="单次课时"
                >
                  <template slot="append">时</template>
                </el-input>
                <template v-else>-</template>
              </td>
              <td class='input-td'>
                <el-input type="text" class="price" v-model="item.price" placeholder="课时单价">
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td class='input-td'>
                <!-- 按期的次数根据日期定 -->
                <template v-if="statusList[index].timesAlert">
                  <div class="times-box">
                    <div class="time-num" @click="openSelect(index)">{{item.times}}</div>
                    <div class="time-text">次</div>
                  </div>
                </template>
                <template v-else-if="!statusList[index].showTimes">-</template>
                <el-input
                  v-else
                  type="text"
                  class="price"
                  :disabled="statusList[index].timesDisabled"
                  v-model="item.times"
                  placeholder="课程次数"
                >
                  <template slot="append">{{statusList[index].timesLabel}}</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input type="text" v-model="item.reduce" class="name" placeholder="直减">
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input type="text" v-model="item.discount" class="name" placeholder="打折折扣 9折为90">
                  <template slot="append">%</template>
                </el-input>
              </td>
              <td class='input-td'>
                <el-input type="text" v-model="item.sundry_fees" class="name">
                  <template slot="append">元</template>
                </el-input>
              </td>
              <td>{{total_price[index]}}</td>
              <td style="width:80px">
                <el-button type="text" @click="delOrder(index)">删除</el-button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="show-total-bar" v-show="orderList.length>0">
          合计：
          <span>{{orderAllTotal}}</span> 元
        </div>
        <div class="btn-wrap" v-show="orderList.length !=0">
          <el-button type="primary" v-if="showOrderInfo" @click="postOrder">提交订单</el-button>
        </div>
      </div>
    </div>
    <v-date-select
      @onChange="selectDayChange"
      @onClose="selectClose"
      :dialog="selectDialog"
      :showBtn="true"
      :info="openItem.info"
    ></v-date-select>
    <v-choose @close="toclose" :dialog="showChoose" @chooseItem="getUpdateCoursePrice"></v-choose>
    <v-un-pay></v-un-pay>
  </div>
</template>

<script>
import { getStuInfo, updateStuInfo, creatStu, creatOrd, updateCoursePrice } from "@/api/student_control";
import { getOrgInfo } from "@/api/operations_center";
import ChooseCour from "./choose_course.vue";
import DateSelect from "./course_date_select/index";
import unPay from "@/components/order/un_pay";
import { mapActions } from "vuex";
export default {
  data() {
    let info = {
      student_name: "",
      student_sex: "",
      contacts: [
        {
          name: "",
          phone: ""
        }
      ],
      remark: "",
      birthday: ""
    };
    return {
      discount_type: '0', // 优惠计算规则 0：先减后折；1：先折后减；默认先减后折
      autoComplete: true, // 智能补全请求是否完成
      emptyInfo: info,
      student_id: "",
      stuInfo: this.$copyObject(info),
      studentName: "",
      showOrder: false,
      showOrderInfo: false,
      showButton: false,
      orderList: [],
      showChoose: false,
      showStu: false,
      fullscreenLoading: false,
      openItem: {
        info: null,
        index: ""
      },
      selectDialog: false,
      typeLabel: this.$store.getters.getAttendTypeLabel,
      timer: null,
      is_inten: false,
      taste_student_id: ''
    };
  },
  components: {
    // 注册子组件
    "v-choose": ChooseCour,
    "v-date-select": DateSelect,
    "v-un-pay": unPay
  },
  created() {
    this.getQrcodeInfo()
    // 意向学员管理 报名点击跳转传入参数
    let query = this.$route.query;
    this.is_inten = query.is_inten;
    this.taste_student_id = query.inten_item.id;
    if (query.is_inten) {
      this.studentName = query.inten_item.student_name;
      this.stuInfo.contacts[0].phone = query.inten_item.phone
    }
  },
  methods: {
    ...mapActions(["getUnPayList"]),
    timeChange(index) {
      let item = this.orderList[index];
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
          this.orderList[index].times = month;
        }
      }
    },
    selectDayChange(day) {
      this.orderList[this.openItem.index].select_day = day;
      this.orderList[this.openItem.index].times = day.length;
    },
    selectClose() {
      this.selectDialog = false;
    },
    openSelect(index) {
      // console.log(JSON.stringify(this.orderList[index]), this.orderList[index]);
      let item = this.orderList[index];
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
    classChange(val, index) {
      let item = this.$copyObject(this.orderList[index]);
      this.orderList.splice(index, 1, item);
    },
    toCreatStu() {
      if (this.student_id == "") {
        if (this.studentName == "") {
          this.$message.error("请选择学生或输入学生姓名");
          return;
        }
        if (this.stuInfo.contacts[0].name == "") {
          this.$message.error("请输入联系人称呼");
          return;
        }
        if (this.stuInfo.contacts[0].phone == "") {
          this.$message.error("请输入联系人电话");
          return;
        }
        this.stuInfo.contacts[0].phone = this.$trim(this.stuInfo.contacts[0].phone);
        // 由后端检测，前端不检测
        // if (!this.$checkPhone(this.stuInfo.contacts[0].phone)) {
        //   this.$message.error("请输入正确的电话号码");
        //   return;
        // }
        let params = this.$copyObject(this.stuInfo);
        params.student_name = this.$trim(this.studentName);
        params.contacts = JSON.stringify(this.stuInfo.contacts);
        if (this.is_inten) {
          params.taste_student_id = this.taste_student_id
        }
        creatStu(params)
          .then(res => {
            this.$message.success("创建成功");
            if (res.errorcode == 0) {
              this.stuInfo.contacts = JSON.parse(params.contacts);
              this.showOrder = true;
              this.student_id = res.data.student_id;
              this.showButton = true;
            }
          })
          .catch(error => {
            this.$message.error(error);
          });
      }
    },
    toChoose() {
      if (this.student_id != "") {
        this.showChoose = true;
      } else {
        this.$message.error("请新建或者选择学生");
      }
    },
    toclose() {
      this.showChoose = false;
      this.showStu = false;
    },
    //获取discount_type 折扣类型 0：先减后折 1：先折后减
    getQrcodeInfo() {
      getOrgInfo()
        .then(res => {
          this.discount_type = res.data.discount_type;
        })
        .catch();
    },
    /**
    * updateCoursePrice
    * 课程模板--更新课程模板的折扣类型
    * @param  Number     {org_id}
    * @param  Number     {course_id}
     * Created by preference on 2019/08/16
     */
    getUpdateCoursePrice (item) {
      let obj = {
        org_id: item.org_id,
        course_id: item.course_id
      }
      console.log('%citem','font-size:40px;color:pink;',item)
      updateCoursePrice(obj)
        .then(res => {
          let list = res.data;
          console.log('%clist','font-size:40px;color:pink;',list)
          item.discount_amount = list.discount_amount;
          item.tuition_fees = list.tuition_fees;
          item.sundry_fees = list.sundry_fees;
          item.sub_total = list.sub_total;
          this.getItem(item);
        })
        .catch(error => {
          this.$message.error(error);
        }); 
    },
    
    getItem(data) {
      this.showOrderInfo = true;
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
        let start_date = obj.start_date / 1;
        let end_date = obj.end_date / 1;
        // 按月收费-长期有效为0，特殊处理
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
      console.log('%cobj','font-size:40px;color:pink;',obj)
      this.orderList.push(obj);
      if (obj.attend_type / 1 === 1) {
        this.openSelect(this.orderList.length - 1);
      }
    },
    getStu(data) {
      // console.log("data", data);
      this.stuInfo = data;
      this.student_id = data.student_id;
      if (this.stuInfo.contacts != null || this.stuInfo.contacts != "") {
        if (this.stuInfo.contacts.length == 1) {
          let obj = {
            name: "",
            phone: ""
          };
          this.stuInfo.contacts.push(obj);
        }
      }
      this.showButton = true;
    },
    //学生选择
    handleSelect(item) {
      this.stuInfo = item;
      this.student_id = item.student_id;
      this.studentName = item.student_name;
      this.showButton = true;
      // 获取未支付订单
      this.getUnPayList({ stu_id: item.student_id });
    },
    //学生搜索
    searchStudent(queryString, cb) {
      this.getStuInfo(queryString, cb);
    },
    getStuInfo(search, cb) {
      window.cancelToken(); // 取消前面未完成的请求
      let params = {
        search,
        page: 1,
        size: 10000
      };
      getStuInfo(params)
        .then(res => {
          cb(res.data.list);
        })
        .catch(e => {
          console.log(e);
        });
    },
    delOrder(index) {
      this.orderList.splice(index, 1);
    },
    postOrder() {
      let student_list = [];
      student_list.push(this.student_id);
      let orderList = this.$copyObject(this.orderList);
      for (let i = 0; i < orderList.length; i++) {
        let item = orderList[i];
        let attend_type = item.attend_type / 1;
        //  一次性收费时间设置为0
        // 按次 start_date、end_date 为空则置 0
        if (attend_type === 0 || (attend_type === 2 && !item.start_date && !item.end_date)) {
          orderList[i].start_date = 0;
          orderList[i].end_date = 0;
        } else if (attend_type !== 1) {
          if (!item.start_date) {
            this.$message.error("请选择" + item.course_name + "的开始日期");
            return;
          }
          if (!item.end_date) {
            this.$message.error("请选择" + item.course_name + "的结束日期");
            return;
          }
          let start = this.$getTimeStamp(item.start_date);
          let end = this.$getTimeStamp(item.end_date);
          if (start > end) {
            this.$message.error(item.course_name + "的开始时间不能大于结束时间");
            return;
          }
          orderList[i].start_date = start;
          orderList[i].end_date = end;
        } else {
          if (item.start_date) {
            orderList[i].start_date = this.$getTimeStamp(item.start_date);
          }
          if (item.end_date) {
            orderList[i].end_date = this.$getTimeStamp(item.end_date);
          }
        }
        orderList[i].canSelectDay = this.$copyObject(orderList[i].time_table);
        orderList[i].time_table = attend_type === 1 ? orderList[i].select_day : [];
        delete orderList[i].select_day;
        delete orderList[i].canSelectDay;
      }
      let obj = {
        student_list: JSON.stringify(student_list),
        course_list: JSON.stringify(orderList)
      };
      this.fullscreenLoading = true;
      creatOrd(obj)
        .then(res => {
          this.fullscreenLoading = false;
          console.log("订单提交成功", res);
          this.$message.success("订单提交成功");
          this.$router.push({
            name: "order_detail_new",
            query: {
              order_id: res.data
            }
          });
        })
        .catch(error => {
          this.fullscreenLoading = false;
          this.$message.error(error);
        });
    },
    reset() {
      this.showButton = false;
      this.studentName = "";
      this.stuInfo = this.$copyObject(this.emptyInfo);
      this.student_id = "";
      this.orderList = [];
    }
  },
  computed: {
    // 课程状态数组
    statusList() {
      let orderList = this.orderList;
      let list = Array.from({ length: orderList.length });
      orderList.map((item, index) => {
        let { attend_type } = item;
        attend_type = attend_type / 1;
        let obj = {
          showTimeRange: false,
          showHours: false,
          showTimes: true,
          timesAlert: false,
          timesLabel: "次",
          showStartTime: true,
          showEndTime: true,
          timesDisabled: false
        };
        switch (attend_type) {
          case 1:
            obj.showTimeRange = true;
            obj.showHours = true;
            obj.timesAlert = true;
            break;
          case 3:
            obj.timesLabel = "月";
            obj.timesDisabled = true;
            break;
          case 0:
            obj.showHours = true;
            // obj.showTimes = false;
            obj.showStartTime = false;
            obj.showEndTime = false;
            break;
        }
        list[index] = obj;
      });
      return list;
    },
    // 课程订单金额数组
    total_price() {
      let total_list = this.orderList.map(item => {
        let { price, hours, times, sundry_fees, reduce, discount } = item;
        let total = 0;
        if (this.discount_type == 0) { // 先减后折 （次数*单次课时*课时单价-直减）*折扣+教材费
          // total = ((Number(times) * Number(hours) * Number(price)) - Number(reduce)) * (Number(discount) /100) + Number(sundry_fees);
          total = price * hours * times - reduce;
          total = total < 0 ? 0 : total;
          total = (total * discount) / 100 + sundry_fees / 1;
        } else { // 先折后减 （次数*单次课时*课时单价*折扣）-直减+教材费
          // total = ((Number(times) * Number(hours) * Number(price)) * (Number(discount) /100)) - Number(reduce) + Number(sundry_fees);
          total = price * hours * times * discount / 100 - reduce;
          total = total < 0 ? 0 : total;
          total = total + sundry_fees / 1;
        }
        // let total = price * hours * times - reduce;
        // // 课程金额最小为 0
        // total = total < 0 ? 0 : total;
        // total = (total * discount) / 100 + sundry_fees / 1;
        return total.toFixed(2);
      });
      return total_list;
    },
    // 订单总金额
    orderAllTotal() {
      if (this.total_price.length == 0) return;
      let total = this.total_price.reduce((a, b) => a / 1 + b / 1);
      return (total / 1).toFixed(2);
    }
  }
};
</script>

<style scoped lang="stylus">
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
  .time-text
    border-left: 1px solid #ebebeb;
    display: table-cell;
    padding: 0 5px;
    border-radius: 0;
    background-color: #f5f7fa;
    color: #909399;
.create-new-student
  padding-top: 20px;
.student-info-wrap
  margin: 0 20px;
  .student-info
    margin-top: 20px;
    margin-bottom: 20px;
    padding-left: 20px;
    .header-bar
      text-align: center;
      font-size: 14px;
      .el-col
        line-height: 32px;
        border: 1px solid #ebebeb;
        border-bottom: none;
    .input-bar
      .el-col
        .el-autocomplete
          width: 100%;
    .btn-bar
      margin-top: 15px;
.order-wrap
  margin: 0 20px;
  padding-bottom: 20px;
  .order-box
    .create-btn
      margin-top: 20px;
      margin-bottom: 20px;
  .show-total-bar
    margin-top: 20px;
    margin-bottom: 20px;
    span
      color: rgb(238, 26, 45);
    text-align: right;
  .btn-wrap
    margin-top: 30px;
    text-align: center;
.list
  width: 100%;
  border: 1px solid #ebebeb;
.list-header
  width: 100%;
  tr
    width: 100%;
  td
    border: 1px solid #ebebeb;
    height: 40px;
    text-align: center;
    border-collapse: collapse;
    vertical-align: middle;
tbody
  td
    min-width: 80px;
    border: 1px solid #ebebeb;
    text-align: center;
    vertical-align: middle;
    min-height: 40px;
    &.input-td
      width:110px;
    &.time-item
      width: 130px;
      font-size: 14px;
      cursor: pointer;
      color: #03a9fe;
      .el-input__inner
        color: #03a9fe;
      &.time-item-large
        width: 200px;
    &.select-item
      .el-select, .el-input
        width: 100px;
        font-size: 14px;
        cursor: pointer;
        color: #03a9fe;
</style>
