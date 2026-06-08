<template>
  <div class="create-new-student index-wrap" v-loading.fullscreen.lock="fullscreenLoading">
    <el-steps
      :active="active"
      finish-status="success"
      class="index-steps"
      :align-center="alignType"
    >
      <el-step> 
        <template slot="description">
          <p class="step-item">录入学员信息</p >
        </template>
      </el-step>
      <el-step>
        <template slot="description">
          <p class="step-item">选择报名课程</p >
        </template>
      </el-step>
      <el-step>
        <template slot="description">
          <p class="step-item">录入结算信息</p >
        </template>
      </el-step>
    </el-steps>
    <div class="student-info-wrap">
      <div class="tips-bar">1.学生信息</div>
      <div class="student-info">
        <div class="student-info-list-wrap">
          <div class="student-info-list">
            <span><i class="red-text">*</i> 学员姓名</span>
            <el-autocomplete
                class="student-list-search"
                v-model="stuInfo.student_name"
                placement="bottom-end"
                :debounce="500"
                :fetch-suggestions="searchStudent"
                placeholder="请输入或搜索学员姓名"
                popper-class="create-student-list"
                @select="handleSelect"
                :disabled="showButton"
              >
                <template slot-scope="{ item }">
                  <p class="info">{{ item.student_name }} - {{ item.contacts[0].phone }}</p>
                </template>
              </el-autocomplete>
              <el-button type="primary" :disabled="showButton" @click="showStuList">选择学员</el-button>
          </div>
          <div class="student-info-list">
            <span><i class="red-text">*</i> 联系人称呼</span>
            <el-autocomplete
              class="inline-input"
              v-model="stuInfo.contacts[0].name"
              :fetch-suggestions="querySearch"
              placeholder="请输入或选择称呼"
              @select="handleSelectCall"
              @focus="handleFocus"
              :disabled="showButton"
            >
              <i
                class="hoo hoo-unfold"
                slot="suffix">
              </i>
            </el-autocomplete>
          </div>
          <div class="student-info-list">
            <el-row>
              <el-col :span="5">
                <span><i class="red-text">*</i> 手机号码</span>
              </el-col>
              <el-col :span="11">
                <el-input
                  type="text"
                  v-model="stuInfo.contacts[0].phone"
                  class="name"
                  placeholder="手机号码"
                  :disabled="showButton"
                ></el-input>
              </el-col>
              <el-col :span="8" style="padding-left: 5px;">
                <el-button type="text" class="blue-text" @click="toCreat" v-show="!showButton">+ 填写更多信息</el-button>
              </el-col>
            </el-row>
          </div>
        </div>
        <div class="student-info-list-save">
          <el-button type="primary" @click="toCreatStu" :disabled="showButton">确认</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
      </div>
    </div>
    <div class="order-wrap" v-if="student_id">
      <div class="order-box">
        <div class="tips-bar">2.选择课程</div>
        <el-button type="primary" class="create-btn" @click="toChoose">添加课程</el-button>
        <v-table-wrap
          noTableTopBar
          noPage
          v-if="orderList.length !=0"
        >
          <el-table
            slot="table"
            v-loading="tableLoading"
            :data="orderList"
            highlight-current-row
            class="pub-table"
            ref="studentTable"
          >
            <el-table-column label="收费类型" width="100" align="center">
              <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
            </el-table-column>
            <el-table-column label="课程名称" width="160" align="left">
              <template slot-scope="scope">{{scope.row.course_name}}</template>
            </el-table-column>
            <el-table-column label="开始日期" width="140" align="center">
              <template slot-scope="scope">
                <el-date-picker
                  v-model="scope.row.start_date"
                  value-format="timestamp"
                  prefix-icon="null"
                  type="date"
                  :clearable="scope.row.attend_type / 1 === 2"
                  class="birthday"
                  style="width:100%"
                  placeholder="选择日期"
                  @change="timeChange(scope.$index)"
                ></el-date-picker>
              </template>
            </el-table-column>
            <el-table-column label="结束日期" width="140" align="center">
              <template slot-scope="scope">
                <el-date-picker
                  v-model="scope.row.end_date"
                  value-format="timestamp"
                  prefix-icon="null"
                  type="date"
                  :clearable="scope.row.attend_type / 1 === 2"
                  style="width:100%"
                  class="birthday"
                  placeholder="选择日期"
                  @change="timeChange(scope.$index)"
                ></el-date-picker>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="单价(元)" align="center">
              <template slot-scope="scope">
                <el-input type="text" v-model="scope.row.price" ></el-input>
              </template>
            </el-table-column>
            <el-table-column label="数量" align="center" width="120">
              <template slot-scope="scope">
                <div class="blue-text" v-if="scope.row.attend_type === '5' || scope.row.attend_type === '1'">
                  {{scope.row.less_times}}课时 &nbsp;&nbsp;
                  <el-button type="text" @click="updateClass(scope.row, scope.$index)">修改</el-button>
                </div>
                <el-input v-model="scope.row.times" v-else-if="scope.row.attend_type === '3'">
                  <template slot="append">月</template>
                </el-input>
                <el-input v-model="scope.row.times" v-else-if="scope.row.attend_type === '2'">
                  <template slot="append">课时</template>
                </el-input>
                <el-input type="text" v-model="scope.row.times" v-else-if="scope.row.attend_type === '4'"></el-input>
              </template>
            </el-table-column>
            <el-table-column label="直减" align="center">
              <template slot-scope="scope">
                <el-input type="text" v-model="scope.row.reduce" ></el-input>
              </template>
            </el-table-column>
            <el-table-column label="折扣" align="center">
              <template slot-scope="scope">
                <el-input type="text" v-model="scope.row.discount" >
                  <template slot="append">%</template>
                </el-input>
              </template>
            </el-table-column>
            <el-table-column label="教材费(元)" align="center">
              <template slot-scope="scope">
                <el-input type="text" v-model="scope.row.sundry_fees" ></el-input>
              </template>
            </el-table-column>
            <el-table-column label="总价(元)" align="center" fixed="right">
              <!-- <template slot-scope="scope">{{scope.row.sub_total}} 元</template> -->
              <!-- <template slot-scope="scope">{{total_now_price(scope.row)}} 元</template> -->
              <template slot-scope="scope">{{total_price[scope.$index]}}</template>
            </el-table-column>
            <el-table-column label="操作" align="center" fixed="right">
              <template slot-scope="scope">
                <el-button type="text" @click="delOrder(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </v-table-wrap>
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
    <v-student-info
      :showStu="showStu"
      :stuInfoData="stuInfoData"
      :editData="stuInfo"
      @handleOK="handleOK"
      @handleCancel="toCloseCreat"
    ></v-student-info>
    <v-student-dialog
      @onClose="closeStuDialog"
      @studentItem="studentItem"
      :dialog="showStuListDialog"
    ></v-student-dialog>
      <!-- :classId="class_id"
      :timetableId="timetable_id" -->
      <!-- :edit-data="rowData" -->
    <!-- 按期收费修改课时-->
    <el-dialog title='修改课时数' width='650px' :visible.sync="showChangeClass">
      <el-row style="line-height: 36px; height: 100px;">
        <el-col :span="3">
          总课时
        </el-col>
        <el-col :span="8" style="padding-right: 10px;">
          <el-input v-model="form.schedule_times" placeholder="课次"> <!--  :disabled="statusData.timesDisable" -->
            <template slot="append">次</template>
          </el-input>
        </el-col>
        <el-col :span="8" style="padding-left: 10px;">
          <el-input v-model="form.hours" placeholder="单次课时">
            <template slot="append">课时/次</template>
          </el-input>
        </el-col>
        <el-col :span="4" class="text-center">
          <span class="gray-text">共计 <i class="black-text">{{totalClassCount}}</i> 课时</span>
        </el-col>
      </el-row>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancleChange">取 消</el-button>
        <el-button type="primary" @click="postChangeClass">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getStuInfo, updateStuInfo, creatStu, creatOrd, updateCoursePrice, createCourseOrder } from "@/api/student_control";
import { getOrgInfo } from "@/api/operations_center";
import ChooseCour from "./choose_course_new.vue";
import DateSelect from "./course_date_select/index";
import unPay from "@/components/order/un_pay";
import { mapActions } from "vuex";
import studentInfo from "./student_info.vue";
import studentListDialog from "./student_list_dialog.vue";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    // let info = {
    //   student_name: "",
    //   student_sex: "",
    //   contacts: [
    //     {
    //       name: "",
    //       phone: ""
    //     }
    //   ],
    //   remark: "",
    //   birthday: ""
    // };
    let info = {
      create_time: "",
      headimage: "",
      student_name: "",
      student_sex: "",
      school: "",
      grade: "",
      join_date: "",
      contacts: [
        // 紧急联系人
        {
          name: "",
          phone: ""
        }
      ],
      email: "",
      birthday: "",
      from: "",
      address: "",
      qq_num: "",
      student_area: "",
      student_id: ""
    };
    return {
      showStuListDialog: false,
      showChangeClass: false,
      tableLoading: false,
      active: 0,
      alignType: true,
      discount_type: '0', // 优惠计算规则 0：先减后折；1：先折后减；默认先减后折
      autoComplete: true, // 智能补全请求是否完成
      emptyInfo: info,
      student_id: "",
      stuInfo: this.$copyObject(info),
      // studentName: "",
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
      taste_student_id: '',
      restaurants: [],
      rowData: [],
      form: {},
      itemIndex: '',
      totalClass: '',
      stuInfoData: {},
    };
  },
  components: {
    // 注册子组件
    "v-choose": ChooseCour,
    "v-date-select": DateSelect,
    "v-un-pay": unPay,
    "v-student-info": studentInfo,
    "v-student-dialog": studentListDialog,
    "v-table-wrap": tableTemplate,
  },
  created() {
    this.getQrcodeInfo()
    // 意向学员管理 报名点击跳转传入参数
    let query = this.$route.query;
    console.log('%c意向学员管理 报名点击跳转传入参数query11122','font-size:40px;color:pink;',query.inten_item)
    this.is_inten = query.is_inten;
    if (query.is_inten) {
      this.taste_student_id = query.inten_item.id;
      this.stuInfo.student_name = query.inten_item.student_name;
      this.stuInfo.contacts[0].phone = query.inten_item.phone
    }
    // 从学员管理 - 在读学员 - 学员详情 列表点击 ‘续费’ 传入参数
    query.student_info = JSON.parse(query.student_info);
    if (query.student_info) {
      this.student_id = query.student_info.contacts.crm_stu_id;
      this.stuInfo.student_name = query.student_info.student_name;
      this.stuInfo.contacts[0].name = query.student_info.contacts.relation;
      this.stuInfo.contacts[0].phone = query.student_info.contacts.phone
      this.showButton = true;
      this.active = 1;
      // 获取未支付订单
      this.getUnPayList({ stu_id: query.student_info.contacts.crm_stu_id });
      // this.handleSelect(query.student_info)
    }
  },
  methods: {
    /**
    * studentItem 选择学员后赋值
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/05
     */
    studentItem (item) {
      item.contacts.forEach(i => {
        i.name = i.relation;
      })
      this.stuInfo = item;
      this.student_id = item.student_id;
      this.stuInfo.student_name = item.student_name;
      this.showButton = true;
      this.active = 1;
      // 获取未支付订单
      this.getUnPayList({ stu_id: item.student_id });
      // this.stuInfo.student_name = item.student_name;
      // if (item.contacts.length != 0) {
      //   this.stuInfo.contacts[0].name = item.contacts[0].relation;
      //   this.stuInfo.contacts[0].phone = item.contacts[0].phone;
      // }
    },
    
    /**
    * updateClass 按期收费 修改课时数
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/02
     */
    updateClass (row, index) {
      this.itemIndex = index;
      this.form = row;
      this.showChangeClass = true;
    },
    
    /**
    * postChangeClass 保存修改课时数
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/02
     */
    postChangeClass () {
      // 将修改后的课时数
      this.$set(this.orderList[this.itemIndex], 'less_times', this.totalClass);
      this.$set(this.orderList[this.itemIndex], 'times', this.form.schedule_times);
      this.showChangeClass = false;
    },

    /**
    * cancleChange  取消 关闭修改课时数弹窗
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/02
     */
    cancleChange () {
      this.showChangeClass = false;
    },
    /**
    * showStuList 学员列表弹窗打开
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/05
     */
    showStuList () {
      this.showStuListDialog = true;
    },
    
    /**
    * closeStuDialog 学员列表弹窗关闭
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/05
     */
    closeStuDialog () {
      this.showStuListDialog = false;
      console.log('%conClose','font-size:40px;color:pink;',this.showStuListDialog)
    },
    
    toCreat() {
      // 新建学员
      // let stuInfoData = this.stuInfo.student_name;
      // stuInfoData.studentName = this.stuInfo.student_name;
      // stuInfoData.name = this.stuInfo.contacts[0].name;
      // stuInfoData.phone = this.stuInfo.contacts[0].phone;
      if (this.stuInfo.student_id != '' || this.stuInfo.student_id === undefined) {
        this.$message.warning('选择的是已添加的学员，请前往学员管理中进行信息修改。');
        return;
      }
      this.stuInfoData = this.stuInfo;
      this.showStu = true;
    },
    toCloseCreat() {
      // 关闭新建学员窗口
      this.rowData = {};
      this.showStu = false;
    },
    handleOK(formData) {
      // 创建或编辑成功的回调
      // this.getStudentList();
      // this.stuInfo.student_name = formData.student_name;
      // this.stuInfo.contacts = formData.contacts;
      this.stuInfo = formData;
      this.showStu = false;

      // this.$message.success(message);
    },
    querySearch(queryString, cb) {
      var restaurants = this.restaurants;
      var results = queryString ? restaurants.filter(this.createFilter(queryString)) : restaurants;
      // 调用 callback 返回建议列表的数据
      cb(results);
    },
    createFilter(queryString) {
      return (restaurant) => {
        return (restaurant.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
      };
    },
    loadAll() { // 联系人称呼 默认数据
      return [
        { "value": "爸爸"},
        { "value": "妈妈"},
        { "value": "爷爷"},
        { "value": "奶奶"},
        { "value": "外公"},
        { "value": "外婆"},
      ];
    },
    handleSelectCall(item) {
      console.log(item);
    },
    /**
    * handleFocus
    * @param  Boolean     {name}
     * Created by preference on 2019/11/19
     */
    handleFocus (item) {
      console.log('%citem','font-size:40px;color:pink;',item)
    },
    
    ...mapActions(["getUnPayList"]),
    timeChange(index) {
      let item = this.orderList[index];
      let { attend_type, start_date, end_date, times } = item;
      attend_type = attend_type / 1;
      const m = this.datemonth(this.$formatToDate(start_date / 1000,'Y-M-D'), this.$formatToDate(end_date / 1000,'Y-M-D')); // 计算开始时间和结束时间之间实际跨了多少个月
      if (attend_type === 3) {
        if (start_date - end_date > 0) {
          this.$message.error("开始日期需要大于结束日期");
        } else if (m - times >= 1 ) {
          this.$message.warning("输入时长与实际的开始/结束时间相差超过一个月");
          this.orderList[index].times = m;
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
    /**
    * datemonth 计算两个日期之间相差的月份数
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
      * Created by preference on 2019/11/07
      */
    datemonth (startDate,endDate) {
      // 拆分年月日
      startDate = startDate.split('-');
      // 得到月数
      startDate = parseInt(startDate[0]) * 12 + parseInt(startDate[1]);
      // 拆分年月日
      endDate = endDate.split('-');
      // 得到月数
      endDate = parseInt(endDate[0]) * 12 + parseInt(endDate[1]);
      let m = Math.abs(startDate - endDate);
      return m;
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
        if (this.stuInfo.student_name == "") {
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
        params.student_name = this.$trim(this.stuInfo.student_name);
        params.contacts = JSON.stringify(this.stuInfo.contacts);
        if (params.birthday != '') {
          params.birthday = new Date(params.birthday).getTime() / 1000;
        } else if (params.join_date != '') {
          params.join_date = new Date(params.join_date).getTime() / 1000;
        }
        if (this.is_inten) {
          params.taste_student_id = this.taste_student_id
        }
        delete params.student_id
        console.log('%cparams','font-size:40px;color:pink;',params)
        creatStu(params)
          .then(res => {
            this.$message.success("创建成功");
            if (res.errorcode == 0) {
              this.stuInfo.contacts = JSON.parse(params.contacts);
              this.showOrder = true;
              this.student_id = res.data.student_id;
              this.showButton = true;
              this.active = 1;
            }
            this.is_inten = false
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
          item.less_times = Number(list.times) * Number(list.hours);
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
      // let item = { isNew: true, select_day: this.$copyObject(date) };
      let item = { isNew: true};
      let start_date = obj.start_date / 1;
      let end_date = obj.end_date / 1;
      // 一次性收费 start_date、end_date 置空
      // 按次 start_date = 0 、end_date = 0 则置空
      if (attend_type === 0 || (attend_type === 2 && start_date === 0)) {
        obj.start_date = "";
        obj.end_date = "";
      } else if (attend_type === 5 || attend_type === 1){ // 按期添加临时字段存times,供修改时课时调用，因为times和less_times都会被修改
        obj.schedule_times = obj.times;
        obj.start_date = this.$getTimeStamp(start_date, 13);
        obj.end_date = this.$getTimeStamp(end_date, 13);
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
      this.stuInfo.student_name = item.student_name;
      this.showButton = true;
      this.active = 1;
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
        item.crm_course_id = item.course_id;
        item.less_times = item.times * item.hours; // 创建订单时，less_time = times
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
        } else if (attend_type === 5 || attend_type === 1) { // 按期收费 最后将最初保存的times传回times，以供保存
          orderList[i].times = orderList[i].schedule_times
        } else {
          if (item.start_date) {
            orderList[i].start_date = this.$getTimeStamp(item.start_date);
          }
          if (item.end_date) {
            orderList[i].end_date = this.$getTimeStamp(item.end_date);
          }
        }
        // orderList[i].canSelectDay = this.$copyObject(orderList[i].time_table);
        // orderList[i].time_table = attend_type === 1 ? orderList[i].select_day : [];
        delete orderList[i].select_day;
        delete orderList[i].canSelectDay;
        delete orderList[i].schedule_times; // 删除临时保存times字段
      }
      let obj = {
        student_list: JSON.stringify(student_list),
        course_list: JSON.stringify(orderList)
      };
      this.fullscreenLoading = true;
      createCourseOrder(obj)
        .then(res => {
          this.fullscreenLoading = false;
          console.log("订单提交成功", res);
          this.$message.success("订单提交成功");
          this.$router.push({
            name: "order_detail_new_again",
            query: {
              order_id: res.data.order_id
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
      this.stuInfo.student_name = "";
      this.stuInfo = this.$copyObject(this.emptyInfo);
      this.student_id = "";
      this.orderList = [];
      this.active = 0;
    }
  },
  computed: {
    // 按期收费 共计课时计算
    totalClassCount(){
      let { schedule_times, hours } = this.form;
      schedule_times = schedule_times ? schedule_times : 0;
      hours = hours ? hours : 0;
      let total = Number(schedule_times) * Number(hours);
      this.totalClass = total;
      return total;
    },
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
    /**
    * total_now_price 计算当前行总价
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/02
     */
    total_now_price() {
      return function(item){ // 闭包传值
        let { price, hours, times, sundry_fees, reduce, discount } = item;
        let total = 0;
        // hours = 1;
        // 现在新版课次（hours）字段 只做按期收费计算共计课时使用，其他处不作使用，所以这里默认设为1

        // 默认先减后折
        total = ((Number(times) * Number(hours) * Number(price)) - Number(reduce)) * (Number(discount) /100) + Number(sundry_fees);

        // if (this.discount_type == 0) { // 先减后折 （次数*单次课时*课时单价-直减）*折扣+教材费
        //   total = ((Number(times) * Number(hours) * Number(price)) - Number(reduce)) * (Number(discount) /100) + Number(sundry_fees);
        // } else { // 先折后减 （次数*单次课时*课时单价*折扣）-直减+教材费
        //   total = ((Number(times) * Number(hours) * Number(price)) * (Number(discount) /100)) - Number(reduce) + Number(sundry_fees);
        // }
        this.$set(item, 'sub_total', total.toFixed(2));
        return total.toFixed(2);
      }
    },
    // 课程订单金额数组
    total_price() {
      let total_list = this.orderList.map(item => {
        let { price, hours, times, sundry_fees, reduce, discount } = item;
        let total = 0;
        // 默认先减后折
        total = ((Number(times) * Number(hours) * Number(price)) - Number(reduce)) * (Number(discount) /100) + Number(sundry_fees);
        // 现在新版去除了课次（hours）字段 现在计算方式是 （课时 * 单价 - 直减）* 优惠 + 教材费；（先减后折，先折后减规则灵活变动，只是去除hours）
        // if (this.discount_type == 0) { // 先减后折 （次数*单次课时*课时单价-直减）*折扣+教材费
        //   total = ((Number(times) * Number(hours) * Number(price)) - Number(reduce)) * (Number(discount) /100) + Number(sundry_fees);
        // } else { // 先折后减 （次数*单次课时*课时单价*折扣）-直减+教材费
        //   total = ((Number(times) * Number(hours) * Number(price)) * (Number(discount) /100)) - Number(reduce) + Number(sundry_fees);
        // }
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
  },
  mounted() {
    this.restaurants = this.loadAll();
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
    text-align: left;
    span
      color: rgb(238, 26, 45);
  .btn-wrap
    margin-top: 30px;
    text-align: left;
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
.student-info-list-wrap
  display flex
  width 1200px
  .student-info-list
    width 390px
    line-height 36px
  .student-info-list:nth-child(1)
    span
      margin-right 5px
  .student-info-list:nth-child(2)
    margin-left 5px
    width 340px
    span
      margin-right 5px
.student-info-list-save
  margin-top 20px
.index-steps
  margin 0 auto 60px auto
  padding-top 60px
  width 724px;
.index-wrap
  padding-bottom 50px
.index-wrap >>> .el-step__head.is-process, .index-wrap >>> .is-wait
  color $gray
  border-color $gray
.index-wrap >>> .el-step__head.is-success
  color #0084ff
  border-color #0084ff
.index-wrap >>> .el-step__head.is-process
  color #0084ff
  border-color #0084ff
.index-wrap >>> .el-step__title.is-process
  color #0084ff
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-success
  margin-top 15px
  color #0084ff
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-process
  margin-top 15px
  font-size 16px
  color #0084ff
.index-wrap >>>  .el-step__description.is-wait
  margin-top 15px
  font-size 16px
.index-wrap >>> .el-step.is-center .el-step__description
  padding-left 10%
  padding-right 10%
.index-wrap >>> .pub-filter-box
  padding 0
.index-wrap >>> .border
  border none !important
.index-wrap >>> .pub-table-wrap
  padding 0
</style>
