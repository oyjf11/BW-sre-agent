<template>
  <div v-loading='fullLoading' class="student-order-details">
    <!-- 学生信息 -->
    <div class='student-info-wrap'>
      <div class="tips-bar">1.学生信息</div>
      <div class='student-info'
           v-if="studentInfo">
        <el-row type='flex'
                class='header-bar'>
          <el-col style='flex:0 0 220px;'>学生姓名</el-col>
          <el-col>联系人称呼</el-col>
          <el-col>电话号码</el-col>
          <el-col>备注</el-col>
        </el-row>
        <el-row type="flex"
                class='input-bar'>
          <el-col style='flex:0 0 220px;'>
            {{studentInfo.student_name}}
          </el-col>
          <el-col>
            {{studentInfo.contacts[0].name}}
          </el-col>
          <el-col>
            {{studentInfo.contacts[0].phone}}
          </el-col>
          <el-col>
            {{studentInfo.remark}}
          </el-col>
        </el-row>
      </div>
    </div>
    <!-- end -->
    <v-course-box  
      @onSubmit='toEidtOrd' 
      :payStatus='payStatus' 
      v-if='Object.keys(orderInfo).length !==0' 
      :info='orderInfo' 
      :discount_type='discount_type'
      :is_modify_teacher='is_modify_teacher'
      ></v-course-box>
    <div class='other-fee'>
      <div class='tips-bar'>3.添加其他收费<p class="tips-text"><i class="hoo hoo-feedback_fill"></i>不再允许录入</p></div>
      <el-button :disabled="true" class='add-btn' >添加其他收费</el-button>
      <!-- <el-button class='add-btn'
                 @click="addOtherFee">添加其他收费</el-button> -->
      <div class='other-fee-list'>
        <el-row type='flex'
                v-for="(fee,inx) in other_fee_list"
                :key='inx'>
          <el-col :span='4'>
            <el-select v-model="fee.title"
                       allow-create
                       default-first-option
                       filterable
                       placeholder="请选择">
              <el-option v-for="item in other_list"
                         :key="item"
                         :label="item"
                         :value="item">
              </el-option>
            </el-select>
          </el-col>
          <el-col :span='3'>
            <el-input placeholder="请输入金额"
                      v-model="fee.amount"></el-input>
          </el-col>
          <el-col :span='2'>
            <el-button type="danger"
                       icon="el-icon-close"
                       @click="deleteFee(inx)"></el-button>
          </el-col>
          <el-col :span='2'
                  v-if='fee.isEffective&&fee.isEffective == true'
                  class='tip'>已生效</el-col>
        </el-row>
        <el-button class='other-fee-submit'
                   type='primary'
                   @click="toEidtOrd()"
                   v-if="other_fee_list.length>0">提交</el-button>
      </div>
    </div>

    <div class='pay-list-wrap'>
      <div class="tips-bar">4.收款记录
        <a href="http://www.lodop.net/download/CLodop_Setup_for_Win32NT_https_3.075Extend.zip"
           download
           class='to-download'>下载打印控件</a>
      </div>
      <div class='pay-show-bar'>
        <div class='pay-total'>
          <i class="fa fa-usd"></i>
          <span style="margin-left: 10px;">
            共计&ensp;{{orderInfo.receivable_total}}元&ensp;|&ensp;差额&ensp;
            <i style="color:#EE1A2D;">{{orderInfo.diff_amount}}元</i>
          </span>
          <span>钱包余额：
            <i style="color:#EE1A2D;">{{balance}}元</i>
          </span>
          <div class="select-teacher">
            <span>&ensp;|&ensp;推荐教师 &ensp;</span>
            <el-select style="width: 200px;" v-model="teacherList.user_id" clearable @change="handleTeacherChange(teacherList.user_id)" placeholder="无">
              <el-option :key="index"
                        :label="item.nickname"
                        :value='item.user_id'
                        v-for="(item,index) in teacherList">
              </el-option>
            </el-select>
          </div>
        </div>
        
      </div>
      <div class='pay-add-wrap'>
        <el-row type='flex'>
          <el-col :span='4'>
            <el-select v-model="addOrderPay.payment"
                       class="price"
                       placeholder="支付方式">
              <el-option v-for='(item,index) in payMethodList'
                         :key='index'
                         :label='item'
                         :value='item'></el-option>
            </el-select>
          </el-col>
          <el-col :span='4'>
            <el-input type="text"
                      class="price"
                      v-model="addOrderPay.amount"
                      :placeholder="addOrderPay.payment!='钱包余额'?'实际交款金额':'最大可用'+balance+'元'"></el-input>
          </el-col>
          <el-col :span='3'>
            <el-input type="text"
                      v-model="addOrderPay.remark"
                      class="remark"
                      placeholder="请输入备注"></el-input>
          </el-col>
          <el-col :span='2'>
            <el-button type="primary"
                       @click.stop.prevent="payMoney">提交</el-button>
          </el-col>
        </el-row>

      </div>
      <el-table class="pay-list"
                :data="orderInfo.pay_list">
        <el-table-column label='选择'>
          <template slot-scope="scope">
            <input type="checkbox"
                   :value="scope.row.payin_id"
                   v-model="pay_select"
                   v-if="scope.row.is_del==0&&(scope.row.apply_id == null && scope.row.apply_status == null) || scope.row.apply_status == 2">
          </template>
        </el-table-column>
        <el-table-column label='付款方式'>
          <template slot-scope="scope">
            {{scope.row.payment}}
            <span v-if='scope.row.payment != "在线支付" &&scope.row.payment != "钱包余额" && scope.row.payment != "微信-付款码支付"'>
              <el-button type='text'
                         @click='showPayType(scope.row)'>修改</el-button>
            </span>
          </template>
        </el-table-column>
        <el-table-column label='收款金额'
                         prop='amount'>
        </el-table-column>
        <el-table-column label='备注'
                         prop='remark'>
          <template slot-scope="scope">
            <span v-if='scope.row.remark'>{{scope.row.remark}}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="收款日期">
          <template slot-scope="scope">
            {{scope.row.created_date|formatToDate("Y-M-D")}}
          </template>
        </el-table-column>
        <el-table-column label="打印次数"
                         prop='print_count'>
        </el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button v-if="scope.row.payment != '在线支付'&&scope.row.print_count>0&&(scope.row.apply_id == null || scope.row.apply_id == 0)&&scope.row.der_id == 0 && scope.row.is_del == 0"
                       type="primary"
                       @click="goApply(scope.row)">申诉</el-button>
            <el-button v-if="scope.row.payment != '在线支付' && scope.row.payment !== wxPayText && scope.row.print_count==0&&(scope.row.apply_id == null || scope.row.apply_id == 0)&&scope.row.is_del==0&&scope.row.der_id == 0"
                       type="primary"
                       @click="canclePay(scope.row)">撤销支付</el-button>
            <!-- 微信-付款码支付不允许撤销 -->
            <div v-if='scope.row.payment === wxPayText && scope.row.print_count==0&&(scope.row.apply_id == null || scope.row.apply_id == 0)&&scope.row.is_del==0&&scope.row.der_id == 0'>-</div>
            <el-button v-if="scope.row.apply_id > 0 && scope.row.apply_status == 0 && scope.row.is_del==0&&(scope.row.der_id == 0||scope.row.der_id > 0)"
                       type="info">申诉中</el-button>
            <el-button v-if="(scope.row.apply_status == 1 || scope.row.is_del==1)&&(scope.row.der_id == 0 || scope.row.der_id>0)"
                       type="danger">已撤销</el-button>
            <el-button v-if="scope.row.apply_status == 2&&(scope.row.der_id == 0||scope.row.der_id > 0)&& scope.row.is_del == 0"
                       type="primary"
                       @click="goReapply(scope.row)">重新申诉</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="text-align: center;margin-top:30px;padding-bottom:20px">
        <el-button @click="handlerPaySelect"
                   v-if="pay_select.length === 0">
          全选
        </el-button>
        <el-button @click="handlerPayNoSelect"
                   v-if="pay_select.length > 0">取消选择</el-button>
        <el-button type="primary"
                   @click="print_preview(pay_select)">
          <i v-if="pay_select.length > 1">合并打印</i>
          <i v-else>打印</i>
        </el-button>
        <el-button @click="newPrint">云打印</el-button>
      </div>
    </div>


    <!--修改支付方式-->
    <el-dialog title='修改支付方式' width='300px' :visible.sync="showChangePayType">
      <el-select v-model="changePaytype"
                 class="price"
                 placeholder="支付方式">
        <el-option v-for='(item,index) in payMethodList'
                   :key='index'
                   :label='item'
                   :value='item'></el-option>
      </el-select>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="cancleChange">取 消</el-button>
        <el-button type="primary"
                   @click="postChangePayType">确 定</el-button>
      </span>
    </el-dialog>

    <div>
      <div v-if="false">
        <object id="LODOP_OB"
                classid="clsid:2105C259-1E0C-4534-8141-A753534CB4CA"
                width=0
                height=0>
          <embed id="LODOP_EM"
                 type="application/x-print-lodop"
                 width=0
                 height=0>
        </object>
      </div>
    </div>
    <!-- 弹出框 -->
    <el-dialog title="补打原因"
               :visible.sync="printAlertDialogVisible"
               class="reason-dialog">
      <div class="flex-block">
        <el-input type="textarea"
                  :rows="2"
                  placeholder="请输入补打原因"
                  v-model="print_remark">
        </el-input>
      </div>

      <div slot="footer"
           class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="print_directly">保存</el-button>
      </div>

    </el-dialog>

    <!-- 打印详情弹出框 -->
    <el-dialog title="打印详情"
               :visible.sync="printLogDetailDialogVisible"
               :before-close="closePrintDetail"
               style="  width:50%; margin: 0 auto;">
      <div v-html="print_detail">
      </div>
      <div slot="footer"
           class="dialog-footer"
           style="text-align:center">
        <el-button @click.prevent.stop="printLogDetailDialogVisible = false">关闭</el-button>
        <el-button type="primary"
                   @click.prevent.stop="print_alert(print_index)">打印</el-button>
      </div>
    </el-dialog>
    <!-- 补打原因弹出框 -->
    <el-dialog title="补打原因"
               :visible.sync="printA4AlertDialogVisible"
               class="reason-dialog">
      <div class="flex-block">
        <el-input type="textarea"
                  :rows="2"
                  placeholder="请输入补打原因"
                  v-model="print_remark">
        </el-input>
      </div>
      <div slot="footer"
           class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="a4_print_confirm">保存</el-button>
      </div>
    </el-dialog>
    <!-- 弹出框 -->
    <el-dialog title="打印原因"
               :visible.sync="multiPrintAlertDialogVisible"
               class="reason-dialog">
      <div class="flex-block">
        <el-input type="textarea"
                  :rows="2"
                  placeholder="请输入批量打印原因"
                  v-model="print_remark">
        </el-input>
      </div>
      <div slot="footer"
           class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="multi_print_directly">保存</el-button>
         <el-button type="primary" @click="newPrint">易联云</el-button>            
      </div>
    </el-dialog>
    <!-- 批量打印弹出框 -->
    <el-dialog title="批量打印原因"
               :visible.sync="multiA4PrintAlertDialogVisible"
               class="reason-dialog">
      <div class="flex-block">
        <el-input type="textarea"
                  :rows="2"
                  placeholder="请输入批量打印原因"
                  v-model="print_remark">
        </el-input>
      </div>
      <div slot="footer"
           class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="a4_print_confirm">保存</el-button>
      </div>
    </el-dialog>
    <div class="print_wrap">
      <!--<object class="print_alert"  id="LODOP_OB" classid="clsid:2105C259-1E0C-4534-8141-A753534CB4CA" width=0 height=0>-->
      <!--<embed id="LODOP_EM" type="application/x-print-lodop" width=0 height=0></embed>-->
      <!--</object>-->

      <div style="position: fixed;left: 40%;top: 40%;width:500px;height: 200px;background: #ebebeb;border-radius: 10px;"
           v-if="showPrintList">
        <i class="fa fa-close"
           style="float: right;margin:15px 25px 0 0;font-size: 20px;"
           @click="closePrintList"></i>
        <el-form ref="form"
                 :model="form"
                 label-width="80px"
                 style="margin-top: 10px;">
          <el-form-item label="选择打印">
            <el-select v-model="form.choose_print"
                       placeholder="请选择"
                       @change="selectPrint(form.choose_print)">
              <el-option v-for="(print) in print_list"
                         :key="print.value"
                         :label="print.name"
                         :value="print.value">
              </el-option>
            </el-select>
          </el-form-item>
          <!--<el-form-item label="打印数量">-->
          <!--<el-input v-model="form.count"></el-input>-->
          <!--</el-form-item>-->
          <el-form-item>
            <el-button type="primary"
                       @click="toPrint">打印</el-button>
            <el-button @click="closePrintList">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <!-- 弹出框 -->
    <el-dialog title="原因"
               :visible.sync="isApply"
               width="30%"
               center>
      <textarea v-model="remark"
                style="width:100%;height:80%"
                rows="8"
                cols="10"></textarea>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="remove()">取 消</el-button>
        <el-button type="primary"
                   @click="save()">确 定</el-button>
      </span>
    </el-dialog>

    <!-- <el-dialog
            title="原因"
            :visible.sync="isReapply"
            width="30%"
            center>
              <p>收款方式：{{selectRows.payment}}</p>
              <p>实际收款：{{selectRows.amount}}元</p>
              <p>确认撤销本次收款？</p>
              <span slot="footer" class="dialog-footer">
                <el-button @click="remove()">取 消</el-button>
                <el-button type="primary" @click="save()">确 定</el-button>
              </span>
          </el-dialog> -->
          <v-push-code v-if='pushCodeShow' @close='pushCodeClose' :payInfo='payInfo'></v-push-code>
  </div>
</template>

<script>
import { getPayMethod } from "@/api/operations_center";
import Print from "@/store/modules/app/print";
import DateFormat from "@/store/modules/app/date";
import { mapState,mapGetters } from "vuex";
import pushCode from "./order_details/pushCode";
import { getTeacherList, getRecommendTeacherList } from "@/api/course_control";
import {
  batchPrintCreate,
  payRecall,
  updatePayment,
  getOtherFee,
  wxRefund
} from "@/api/order";
import {
  orderDetail,
  addFee,
  stuDetail,
  editOrd,
  updateStuInfo,
  getStudentLog 
} from "@/api/student_control";
import { apply, reapply, cancel, postPrint} from "@/api/financial";
import { getOrgInfo } from "@/api/operations_center";
import courseBox from "./order_details/course_box";
export default {
  data() {
    return {
      wxPayText:"微信-付款码支付",
      postIng:false,
      pushCodeShow:false,
      payInfo:{},
      payMethodList: [],
      fullLoading:false,
      studentLogList: null,
      student_id: "",
      orderInfo: {},
      addOrderPay: {
        amount: "",
        payment: "",
        remark: ""
      },
      canEdit: false,
      studentInfo: null,
      orderView: [], // 首页整个对象
      LODOP: "",
      mini_app_qrcode: {}, //qrcode
      discount_type: '0', // 优惠计算规则 0：先减后折；1：先折后减；默认先减后折
      pay_select: [],
      printList: [], //打印记录
      printLogDialogVisible: false, //打印纪录对话框
      printLogDetailDialogVisible: false, //打印详情对话框
      printAlertDialogVisible: false, //补打原因对话框
      printA4AlertDialogVisible: false, //A4补打原因对话框
      multiPrintAlertDialogVisible: false, //批量打印
      updateRemarkDialogVisble: false, //修改备注
      updatePaymentDialogVisble: false, //修改支付方式
      multiA4PrintAlertDialogVisible: false, //A4批量打印
      a4PrintPreview: true, //打印预览
      print_detail: "", //打印详情
      print_remark: "", //打印原因
      print_log_sn: "", //打印流水
      print_index: "", //打印当前的位置
      current_remark: "", //选择的备注
      current_payment: "", //选择的收款方式
      current_pay_id: "", //选择的Pay ID
      logo_url: "", //公司logo
      org_name: "", //公司名
      qrcode: {},
      a4PayList: [], //A4预览数组
      pay_map: {}, //支付map集合
      history_list: [],
      showPrintList: false, //是否显示选择打印机列表
      print_list: [], //打印机列表
      form: {
        choose_print: "", //选择中的打印机
        print_count: 1
      },
      balance: 0,
      selectRows: {},
      isApply: false,
      handleType: 0,
      remark: "",
      showChangePayType: false, //是否显示修改支付方式弹窗
      changePaytype: "", //要修改的支付方式
      changeItem: {},
      other_list: [], //收费项目字段列表
      other_fee_list: [], //其他费用列表
      printIndex: 0, //默认第一个打印机
      teacherList: [], // 教师列表
      recommend_teacher_id: '', // 选中的教师ID
      recommend_teacher_type: 0, // 推荐教师切换类型
      is_modify_teacher: 0,
      recommend_teacher:[],
    };
  },
  created() {
    this.getPayMethod();
    this.otherFee();
    this.$store.dispatch("setTopTitle", {
      title: "订单详情",
      des: "订单详情"
    });
  },
  components: {
    "v-course-box":courseBox,
    "v-push-code":pushCode
  },
  methods: {
    handleTeacherChange(e) {
      this.recommend_teacher_id = e;
      this.recommend_teacher_type = 1
      this.is_modify_teacher = 1;
      this.toEidtOrd();
    },
    teacherLabel(list) {
      list.forEach(item => {
        item.showLabel = item.teacher_name + " - " + item.class_name;
      });
      return list;
    },
    getTeacherAll() {
      getRecommendTeacherList({})
        .then(res => {
          // this.lessionData.list = this.teacherLabel(res.data.list);
          let idList = [];
          res.data.list.forEach(item => {
            idList.push(item.user_id);
          })
          let recommend_teacher = '';
          if (this.recommend_teacher_id > 0) {
            recommend_teacher = this.recommend_teacher;
            if (recommend_teacher != '' && recommend_teacher != [] && recommend_teacher.length != 0) {
              if (idList.indexOf(recommend_teacher.user_id) == -1) {
                res.data.list.push(recommend_teacher);
              }
            }
            this.teacherList.user_id = this.recommend_teacher_id;
          }
          let teacherList = this.teacherLabel(res.data.list);
          this.teacherList = teacherList;
          // 0: 没有选推荐老师
          if (this.recommend_teacher_id > 0) {
            this.teacherList.user_id = this.recommend_teacher_id;
          }
          console.log("教师列表", this.teacherList);
        })
        .catch(e => {
          console.log(e);
        });
    },
    pushCodeClose(status){
      this.pushCodeShow= false;
      if(status === true){
        this.addOrderPay = {
            payment: "",
            remark: "",
            amount: ""
          };
        this.getOrderDetail();
      }
    },
    getPayMethod() {
      getPayMethod({ attr_name: "payment" })
        .then(res => {
          this.payMethodList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    goApply(rows) {
      this.selectRows = rows;
      this.isApply = true;
      this.handleType = 1;
    },
    //获取其他收费项目收费列表
    otherFee() {
      let obj = {
        attr_name: "other_fee"
      };
      getOtherFee(obj)
        .then(res => {
          // console.log("other_fee", res);
          this.other_list = res.data.other_fee;
        })
        .catch(error => {
          console.log(error);
        });
    },
    //增加其他费用的收费
    addOtherFee() {
      let obj = { title: "", amount: "",isNew:true };
      this.other_fee_list.push(obj);
    },
    // 检查其他收费
    checkFeeList(){
      let titleArr = [];
      let amountArr = [];
      let titleStatus = true;
      let amountStatus = true;
      let other_fee_list = this.other_fee_list;
      other_fee_list.forEach((i,index)=>{
        if(!i.title){
          titleStatus = false;
          titleArr.push(index+1);
        }
        if(!i.amount || !this.$checkNum(i.amount) || i.amount <0){
          amountStatus = false;
          amountArr.push(index+1)
        }
      })
      let str = "";
      if(!titleStatus){
        str += `<p>请输入或选择第${titleArr.join("、")}行的名称</p>`
      }
      if(!amountStatus){
        str += `<p>第${amountArr.join("、")}行的金额需大于0的数字</p>`
      }
      if(str!==""){
        this.$notify({
          type:"error",
          title:"其他收费错误信息",
          dangerouslyUseHTMLString: true,
          message: str
        });
      }
      return titleStatus&amountStatus;
    },
    //删除其他费用的收费
    deleteFee(inx) {
      let item = this.other_fee_list[inx];
      if(item.isNew === true){
        this.other_fee_list.splice(inx, 1);
        return;
      }
      if(window.$hoo_desk_open !== true && !this.checkFeeList()) return
      this.$confirm("此操作将删除该项费用, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          this.other_fee_list.splice(inx, 1);
          this.toEidtOrd();
        })
        .catch(e => {
          console.log("e",e);
          if(e !== 'cancel') this.$message.error(e);
        });
    },
    canclePay(item) {
      let type = item.payment === this.wxPayText ? 1:0;
      //type 1 微信退款 type 0  
      let confirmText = type === 1 ? '确定要退款吗?':"确定撤销该支付吗?";
      this.$confirm(confirmText, "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        let obj = {
          payin_id: item.payin_id,
          order_id: item.order_id
        };
        if(type === 1){
          return wxRefund(obj);
        }else{
          return payRecall(obj)
        }
      }).then(res=>{
        if(res){
          for (let i = 0; i < this.pay_select.length; i++) {
            if (item.payin_id == this.pay_select[i]) {
              this.pay_select.splice(i, 1);
              break;
            }
          }
          let str = type === 1 ?  "退款" :"撤销";
          this.$message.success(`${str}成功`);
          this.init();
        }
      }).catch(e=>{
        console.log('error',e);
        if(e === "cancel") return;
        this.$message.error(e);
      })
    },
    showPayType(item) {
      // console.log("修改支付方式", item);
      this.changeItem = item;
      this.showChangePayType = true;
    },
    postChangePayType() {
      if(this.changePaytype == "微信-付款码支付"){
        this.$message.error("不能修改成 微信-付款码支付")
        return;
      }
      if (
        this.changePaytype == "钱包余额" &&
        this.changeItem.amount - this.balance > 0
      ) {
        this.$message.error("钱包余额不足！");
        return false;
      }
      console.log("确认修改支付方式");
      let obj = {
        payin_id: this.changeItem.payin_id,
        payment: this.changePaytype
      };
      updatePayment(obj)
        .then(res => {
          this.$message.success("修改成功");
          this.getOrderDetail();
          this.cancleChange();
        })
        .catch(error => {
          this.$message.error("修改失败");
        });
    },
    cancleChange() {
      this.showChangePayType = false;
    },

    goReapply(rows) {
      console.log("rows", rows);
      this.selectRows = rows;
      this.isApply = true;
      this.handleType = 2;
    },

    remove() {
      this.selectRows = {};
      this.isApply = false;
      this.remark = "";
      this.handleType = 0;
    },
    //保存申述
    save() {
      if (!this.remark) {
        this.$message.error("请输入申述原因");
        return;
      }
      if (this.handleType == 1) {
        this.apply();
      }

      if (this.handleType == 2) {
        this.reapply();
      }
    },
    //取消 
    cancel() {
      if (this.selectRows.apply_id == 0 || this.selectRows.apply_id == null) {
        return false;
      }
      let obj = {
        id: this.selectRows.apply_id
      };
      cancel(obj)
        .then(res => {
          this.init();
          this.remove();
        })
        .catch(error => {
          this.remove();
        });
    },
  //申述
    apply() {
      let obj = {
        order_id: this.selectRows.payin_id,
        remark: this.remark
      };
      if(this.postIng) return;
      this.postIng = true;
      apply(obj)
        .then(res => {
          this.init();
          this.remove();
          this.postIng = false;
        })
        .catch(error => {
          this.remove();
          this.postIng = false;
        });
    },
  //重新申述 
    reapply() {
      console.log("this.selectRows", this.selectRows);
      if (this.selectRows.apply_id == 0 || this.selectRows.apply_id == null) {
        return false;
      }
      let obj = {
        id: this.selectRows.apply_id,
        remark: this.remark
      };
      if(this.postIng) return;
      this.postIng = true;
      reapply(obj)
        .then(res => {
          this.init();
          this.remove();
          this.postIng = false;
        })
        .catch(error => {
          this.remove();
          this.postIng = false;
        });
    },
   //匹配男女 
    formatSex(value) {
      let array = { m: "男", f: "女", u: "无" };
      return array[value];
    },
    //付钱
    payMoney() {
      // console.log(this.addOrderPay);
      if (!this.addOrderPay.payment) {
        this.$message.error("请选择支付方式");
        return;
      }
      if (!this.addOrderPay.amount) {
        this.$message.error("请输入收款金额");
        return;
      }
      if (this.addOrderPay.amount / 1 === 0) {
        this.$message.error("请输入大于0的收款金额");
        return;
      }
      if (
        this.addOrderPay.payment == "钱包余额" &&
        this.addOrderPay.amount - this.balance > 0
      ) {
        this.$message.error("钱包余额不足！");
        return;
      }
      if(this.addOrderPay.payment === this.wxPayText){
        this.pushCodeShow = true;
        this.payInfo = Object.assign(this.addOrderPay, {
          order_id: this.$route.query.order_id
        });
        return;
      }
      let obj = Object.assign(this.addOrderPay, {
        order_id: this.$route.query.order_id
      });
      this.fullLoading = true;
      addFee(obj)
        .then(res => {
          this.fullLoading = false;
          this.$message.success("费用提交成功");
          this.addOrderPay = {
            payment: "",
            remark: "",
            amount: ""
          };
          this.getOrderDetail();
        })
        .catch(error => {
          this.fullLoading = false;
          this.$message.error(error);
        });
    },
    //获取学生详情
    getStuDetail() {
      stuDetail(this.student_id)
        .then(res => {
          this.studentInfo = res.data;
          this.balance = res.data.balance;
          if (this.balance == 0.0) {
            this.balance = 0;
          }
          if (this.studentInfo.contacts.length == 1) {
            let obj = {
              name: "",
              phone: ""
            };
            this.studentInfo.contacts.push(obj);
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    //编辑订单 
    toEidtOrd(courseData) {
      if(window.$hoo_desk_open !== true && !this.checkFeeList()) return
      let courseList;
      if(courseData){
        courseList = courseData;
      }else{
        courseList = this.$copyObject(this.orderInfo.course_list);
        courseList.forEach(item=>{
          item.start_date = this.$getTimeStamp({time:item.start_date});
          item.end_date = this.$getTimeStamp({time:item.end_date});
        })
        courseList = JSON.stringify(courseList)
      }
      let obj = {
        order_id: this.$route.query.order_id,
        course_list: courseList,
        recommend_teacher_id: this.recommend_teacher_id
      };
      if (this.other_fee_list.length > 0) {
        obj.other_list = JSON.stringify(this.other_fee_list);
      }
      this.fullLoading = true;
      editOrd(obj)
        .then(res => {
          this.getOrderDetail();
          if (this.recommend_teacher_type = 1) {
            this.$message.success('操作成功');
          } else {
            this.$message.success(res.msgs);
          }
          this.fullLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.getOrderDetail();
          this.fullLoading = false;
        });
    },
    //支付选项
    handlerPaySelect() {
      this.pay_select = [];
      for (let i = 0; i < this.orderInfo.pay_list.length; i++) {
        if (
          (this.orderInfo.pay_list[i].apply_id > 0 &&
            (this.orderInfo.pay_list[i].apply_status == 0 ||
              this.orderInfo.pay_list[i].apply_status == 1)) ||
          this.orderInfo.pay_list[i].is_del == 1
        ) {
          continue;
        }

        this.pay_select.push(this.orderInfo.pay_list[i].payin_id);
      }
    },

    handlerPayNoSelect() {
      this.pay_select = [];
    },

    // ————————————————————————————————————————————————分割线——————————————————————————————————————————
    //老打印初始化
    init() {
      this.printLogDialogVisible = false; //打印纪录对话框
      this.printLogDetailDialogVisible = false; //打印详情对话框
      this.printAlertDialogVisible = false; //补打原因对话框
      this.multiPrintAlertDialogVisible = false;
      this.printA4AlertDialogVisible = false;
      this.multiA4PrintAlertDialogVisible = false;
      this.a4PrintPreview = true;
      this.pay_map = new Map();
      console.log("user", this.getUser.user_name);

      this.getOrderDetail();
      this.getQrcodeInfo();
      //初始化打印机
      if (Print.needCLodop()) {
        var head =
          document.head ||
          document.getElementsByTagName("head")[0] ||
          document.documentElement;
        var oscript = document.createElement("script");
        var ishttps = 'https:' == document.location.protocol ? true: false;
        if(ishttps){
            oscript.src = 'https://localhost:8443/CLodopfuncs.js?priority=1'
        }else{
            oscript.src = "http://localhost:8000/CLodopfuncs.js?priority=1";
        }
        head.insertBefore(oscript, head.firstChild);
        //引用双端口(8000和18000）避免其中某个被占用：
        oscript = document.createElement("script");
        if(ishttps){
            oscript.src = 'https://localhost:8444/CLodopfuncs.js?priority=0'
        }else{
            oscript.src = "http://localhost:18000/CLodopfuncs.js?priority=0";
        }
        head.insertBefore(oscript, head.firstChild);
      }
    },
    //关闭打印详情
    closePrintDetail() {
      console.log("关闭");
      this.printLogDetailDialogVisible = false;
    },
    isEmpty(obj) {
      // null and undefined are "empty"
      if (obj == null) return true;

      // Assume if it has a length property with a non-zero value
      // that that property is correct.
      if (obj.length > 0) return false;
      if (obj.length === 0) return true;

      // If it isn't an object at this point
      // it is empty, but it can't be anything *but* empty
      // Is it empty?  Depends on your application.
      if (typeof obj !== "object") return true;

      // Otherwise, does it have any properties of its own?
      // Note that this doesn't handle
      // toString and valueOf enumeration bugs in IE < 9
      for (var key in obj) {
        if (hasOwnProperty.call(obj, key)) return false;
      }

      return true;
    },
    // 处理打印学科字段
    processPrintSubjectName(courseList){
      var obj = []
      courseList = courseList.map(item=>{
        obj[item.subject_name] = (obj[item.subject_name] || 0) + 1
        item.subject_name_print = item.subject_name + obj[item.subject_name]
        // console.log(item.subject_name_print)
        return item
      })
      return courseList
    },

    // 注册方法----——————————————————————————————（获取打印详情）1
    getOrderDetail() {
      this.fullLoading = true;
      // is_course_order == 1 是从课程订单 点击编辑进入的，会多传一个org_id字段 来替换现有当前org_id
      let data = {};
      if (this.$route.query.is_course_order == 1) {
        data = {
          order_id: this.$route.query.order_id,
          org_id: this.$route.query.org_id
        }
      } else {
        data = {
          order_id: this.$route.query.order_id
        }
      }
      orderDetail(data)
        .then(res => {
          console.log("订单详情", res.data);
          this.orderInfo = res.data;
          this.student_id = res.data.stu_id;
          this.getStuDetail();
          if (this.orderInfo.other_list.length != 0) {
            this.orderInfo.other_list.forEach(
              item => (item.isEffective = true)
            );
          }
          this.other_fee_list = this.orderInfo.other_list;
          console.log("asd",this.other_fee_list)
          this.orderView = res.data;
          let courseList = this.processPrintSubjectName(this.orderView.course_list);
          this.orderView.course_list = courseList;
          console.log('课程列表',courseList);
          this.history_list = this.orderView.course_history;
          for (var i in this.orderView.pay_list) {
            var pay_detail = this.orderView.pay_list[i];
            var pay_id = this.orderView.pay_list[i].payin_id;
            this.pay_map.set(pay_id, pay_detail);
            this.$set(this.orderView.pay_list[i], "select", false);
          }
          this.recommend_teacher_id = res.data.recommend_teacher_id;
          // 获取已离职教师
          this.recommend_teacher = res.data.recommend_teacher;
          this.fullLoading = false;
          this.getTeacherAll();
        })
        .catch(error => {
          this.$message.error(error);
          this.fullLoading = false;
        });
    },

    /**
     * 打印相关
     */
    show_print_detail(content) {
      this.print_detail = content;
      this.printLogDetailDialogVisible = true;
      this.printLogDialogVisible = false;
    },
    //补打打印原因
    print_alert(index) {
      var result = Print.getLodop(
        document.getElementById("LODOP_OB"),
        document.getElementById("LODOP_EM")
      );
      if (result == undefined) {
        this.$confirm(
          "未安装打印机驱动，请点击按照页面顶部提示安装。安装后刷新页面即可打印",
          "请安装打印机驱动",
          {
            confirmButtonText: "确定",
            type: "warning"
          }
        ).then(() => {});
        return false;
      }
      let print_count = parseInt(this.pay_map.get(index[0]).print_count);
      this.print_index = index;
      if (print_count != 0) {
        this.printAlertDialogVisible = true;
      } else {
        this.print_directly();
      }
      this.CreatePrinterList();
    },
    //批量打印提醒
    multi_print_alert() {
      if (this.multipleSelection.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }
      console.log(this.multipleSelection);
      this.multiPrintAlertDialogVisible = true;
    },
    //批量打印
    multi_print_directly() {
      if (this.multipleSelection.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }

      if (this.print_remark == "") {
        this.$message.error("原因不能为空");
        return;
      }
      this.choose_print(this.multipleSelection);
    },
    //获取小程序二维码
    getQrcodeInfo() {
      getOrgInfo()
        .then(res => {
          this.mini_app_qrcode = res.data.mini_app_qrcode;
          this.discount_type = res.data.discount_type;
        })
        .catch();
    },
    getSelectedf() {
      if (this.form.choose_print != "") return this.form.choose_print;
      else return -1;
    },
    //直接打印
    print_directly() {
      let index = this.print_index;
      let print_count = parseInt(this.pay_map.get(index[0]).print_count);
      console.log(print_count);
      if (this.print_remark == "" && print_count != 0) {
        this.$message.error("原因不能为空");
        return;
      }
      this.printAlertDialogVisible = false;
      this.printLogDetailDialogVisible = false;
      // if(){

      // }
      this.showPrintList = true; //显示打印窗口
      this.print_log_sn = this.randomString(6);
      //         this.choose_print(index);
      //        this.createOneFormPage(index,true);
      //        this.form.choose_print
      //        LODOP.PRINT();
    },
    //打印窗口的打印按钮
    toPrint() {
      LODOP = Print.getLodop();
      let index = this.print_index;
      let print_count = parseInt(this.pay_map.get(index[0]).print_count);
      console.log(print_count);
      if (this.print_remark == "" && print_count != 0) {
        this.$message.error("原因不能为空");
        return;
      }
      //        this.getPrintText();
      this.createOneFormPage(index, true);
    },
    //      打印窗口的取消按钮
    canclePrint() {
      this.showPrintList = false; //隐藏示打印窗口
    },

    /**
     * 随机数
     * @param  {[type]} length [description]
     * @return {[type]}        [description]
     */
    randomString(length) {
      var chars = "0123456789".split("");

      if (!length) {
        length = Math.floor(Math.random() * chars.length);
      }

      var str = "";
      for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
      }

      let dateStr = DateFormat.formatDate(new Date(), "yyMMddhhmm");
      return dateStr + str;
    },
    show_print_log(index) {
      this.printList = [];
      let printObj = {
        api: "printList",
        data: {
          payin_id: this.orderView.pay_list[index].payin_id
        }
      };
      this.$store
        .dispatch("fetchAllList", printObj)
        .then(json => {
          this.printList = json.data.list;
        })
        .catch(error => {
          this.$message.error(error);
        });

      this.printLogDialogVisible = true;
    },
    // 打印
    print_preview() {
      let index = this.pay_select;
      if (index.length == 0) {
        this.$message.error("请选择需要打印的记录");
        console.log("index", index);
        return false;
      }
      //转换成数组
      index.sort((a, b)=>{
        return a - b;
      });
      let content = this.getPrintText(index);
      this.print_index = index;
      this.show_print_detail(content);
    },
    // 创建打印机列表
    CreatePrinterList() {
      //        if (document.getElementById('PrinterList').innerHTML!="") return;
      let LODOP = Print.getLodop();
      var iPrinterCount = LODOP.GET_PRINTER_COUNT();
      let print_list = [];
      for (var i = 0; i < iPrinterCount; i++) {
        //          var option=document.createElement('option');
        let print_item = {
          name: LODOP.GET_PRINTER_NAME(i),
          value: i
        };
        //          option.innerHTML=LODOP.GET_PRINTER_NAME(i);
        //          option.value=i;
        //          document.getElementById('PrinterList').appendChild(option);
        print_list.push(print_item);
      }
      this.print_list = print_list;
    },

    a4_print_preview(index) {
      var ishttps = 'https:' == document.location.protocol ? true: false;
      console.log('打印https',ishttps)
      if (index.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }
      index.sort(function(a, b) {
        return a - b;
      });
      let pay_list = [];
      for (var i of index) {
        let pay_record = this.pay_map.get(i);
        pay_list.push(pay_record);
      }
      this.print_index = index;
      this.a4PayList = pay_list;
      this.a4PrintPreview = false;
    },
    // A4打印弹窗
    a4_print_alert() {
      var result = Print.getLodop(
        document.getElementById("LODOP_OB"),
        document.getElementById("LODOP_EM")
      );
      if (result == undefined) {
        this.$confirm(
          "未安装打印机驱动，请点击按照页面顶部提示安装。安装后刷新页面即可打印",
          "请安装打印机驱动",
          {
            confirmButtonText: "确定",
            type: "warning"
          }
        ).then(() => {});
        return false;
      }

      let pay_ids = this.print_index;
      var ishttps = 'https:' == document.location.protocol ? true: false;
      console.log('打印https',ishttps)
      if (pay_ids.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }

      let print_count = parseInt(this.pay_map.get(pay_ids[0]).print_count);

      if (pay_ids.length == 1 && print_count != 0) {
        //查看是否打印过

        this.printA4AlertDialogVisible = true;
        return false;
      } else if (pay_ids.length >= 2) {
        //是否批量打印
        this.multiA4PrintAlertDialogVisible = true;
        return false;
      }

      this.a4_print_confirm();
    },
    // A4打印确认
    a4_print_confirm() {
      let pay_ids = this.print_index;

      console.log(pay_ids);

      if (pay_ids.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }
      let print_count = parseInt(this.pay_map.get(pay_ids[0]).print_count);

      if (pay_ids.length == 1 && print_count != 0 && this.print_remark == "") {
        //查看是否打印过
        this.$message.error("原因不能为空");
        return false;
      } else if (pay_ids.length >= 2 && this.print_remark == "") {
        //是否批量打印
        this.$message.error("原因不能为空");
        return false;
      }

      var result = Print.getLodop(
        document.getElementById("LODOP_OB"),
        document.getElementById("LODOP_EM")
      );
      if (result == undefined) {
        this.$confirm(
          "未安装打印机驱动，请点击按照页面顶部提示安装。安装后刷新页面即可打印",
          "请安装打印机驱动",
          {
            confirmButtonText: "确定",
            type: "warning"
          }
        ).then(() => {});
        return false;
      }

      this.print_log_sn = this.randomString(6);
      this.LODOP = Print.getLodop();
      var status = this.LODOP.SELECT_PRINTER();
      var vm = this;
      if (LODOP.CVERSION) {
        LODOP.On_Return = function(TaskID, Value) {
          console.log("printIndex:" + Value + ";TaskID" + TaskID);
          if (Value == -1) open_type = 0;
          if (Value > -1) {
            vm.createOneA4FormPage(pay_ids, Value);
            LODOP.PRINT();
          }
          // ajax 写入打印次数、打印时间、打印人、打印订单；
          // 修改全局打印次数+=value；
        }.bind(this);
      }
    },
    // 打印内容
    getPrintText(index) {
      var printTest = "";
      if (this.logo_url.is_show) {
        printTest =
          '<div><img style="vertical-align:middle" width="50" height="50" src="' +
          this.logo_url.image_url +
          '"/><span style="margin-left: 5px; font-weight:bold;" >' +
          this.org_name +
          '</span></div><dd style="border-top:1px solid #333;margin:2px 0">';
      }
      printTest += "<h1><b>学生：</b> " + this.orderView.student_name + "</h1>";

      if (this.orderView.school != "" && this.orderView.school != null) {
        printTest += "<p><b>学校：</b> " + this.orderView.school + "</p>";
      }

      printTest +=
        "<p><b>校区：</b> " +
        this.orderView.org_name +
        '</p><div><h1 style="text-align:left;font-size:16px;font-weight:bold">课程明细：</h1>';

      for (let i = 0; i < this.orderView.course_list.length; i++) {
        let course = this.orderView.course_list[i];
        let original_price =
          parseFloat(course.price) *
          parseFloat(course.times) *
          parseFloat(course.hours);
        let discount_price =
          parseFloat(course.reduce) + parseFloat(course.discount_amount);
        let str_discount = "";
        if (parseFloat(discount_price) != 0) {
          str_discount =
            "－优惠￥" +
            parseFloat(discount_price) +
            "元＝折后￥" +
            parseFloat(course.tuition_fees) +
            "元";
        }

        if (
          course.sundry_fees != null &&
          course.sundry_fees != "" &&
          course.sundry_fees != 0 &&
          course.sundry_fees
        ) {
          printTest +=
            '<dl class="courselist"><dd>' +
            course.subject_name_print +
            "(共" +
            (course.attend_type == 1? Number(course.hours)*course.times:course.times) +
            "课时)" +
            "</dd><dd>原价￥" +
            parseFloat(original_price) +
            "元" +
            str_discount +
            "</dd><dd>教材费￥" +
            parseFloat(course.sundry_fees) +
            "元</dd><dd>小计￥" +
            parseFloat(course.sub_total) +
            "元</dd></dl>";
        } else {
          printTest +=
            '<dl class="courselist"><dd>' +
            course.subject_name_print +
            "(共" +
            (course.attend_type == 1? Number(course.hours)*course.times:course.times) +
            "课时)" +
            "</dd><dd>原价￥" +
            parseFloat(original_price) +
            "元" +
            str_discount +
            "</dd><dd>小计￥" +
            parseFloat(course.sub_total) +
            "元</dd></dl>";
        }
      }

      let total_price =
        parseFloat(this.orderView.total_tuition_fees) +
        parseFloat(this.orderView.total_sundry_fees);
      //优惠金额为0时 不显示
      let str_other_discount = "";
      if (parseFloat(this.orderView.total_other_offers) != 0) {
        str_other_discount =
          "<dd>其它费用：<b>￥" +
          parseFloat(this.orderView.total_other_offers) +
          "元</b></dd>";
      }

      printTest +=
        '<dl class="courselist" style="font-size:14px"><dd>合计学费：<b>￥<span>' +
        parseFloat(total_price) +
        "</span>元</b></dd>" +
        str_other_discount +
        "<dd>应交金额：<b>￥" +
        parseFloat(this.orderView.receivable_total) +
        "元</b></dd></dl>";

      if (this.orderView.other_list.length) {
        printTest +=
          '<div style="font-weight:400;color:#333;text-align:right">（ 其它费用明细： ';
        for (let i = 0; i < this.orderView.other_list.length; i++) {
          let other = this.orderView.other_list[i];
          printTest += other.title + ":" + other.amount + "元 ";
        }
        printTest += "）</div>";
      }

      printTest +=
        '</div><h1 style="text-align:left;font-size:16px;font-weight:bold"">收款明细：</h1>';
      let pay_count = 0;
      //收款记录
      let pay_object = new Array();
      index.sort(function(a, b) {
        return a - b;
      });
      for (var i of index) {
        console.log("执行:" + i);
        var ishttps = 'https:' == document.location.protocol ? true: false;
        console.log('打印https',ishttps)
        if (this.isEmpty(i)) {
          continue;
        }
        let pay_detail = this.pay_map.get(i);
        console.log(pay_detail);
        if (pay_object["amount"] == null) {
          pay_object["amount"] = 0;
          pay_object["pay_detail"] = "";
        } else {
          //            console.log('前',pay_object['amount'])
          //            pay_object['amount'] = Number(pay_object['amount'].toString().match(/^\d+(?:\.\d{0,2})?/))
          //            console.log('后',pay_object['amount'])
        }
        pay_object["created_user"] = pay_detail.created_user;
        pay_object["created_date"] = DateFormat.formatDate(
          new Date(pay_detail.created_date * 1000),
          "yyyy-MM-dd"
        );
        //          console.log('pay_detail.amount',pay_detail.amount, pay_object['amount']);
        pay_object["amount"] =
          Number(pay_object["amount"]) + Number(pay_detail.amount);
        pay_object["amount"] = pay_object["amount"].toFixed(2);
        pay_object["pay_detail"] +=
          pay_detail.payment + ":" + pay_detail.amount + "元;";
        pay_object["remark"] = pay_detail.remark;
        pay_object["diff_amount"] = Number(pay_detail.diff_amount).toFixed(2);
      }
      // for (var i of index) {
      //   pay_count ++;
      //  let   pay_detail = this.pay_map.get(i);
      printTest +=
        '<div id="selectPrint"><dl class="courselist" style="font-size:14px"><dd>收款人：<b>' +
        pay_object["created_user"] +
        "</b></dd><dd>收款时间：<b>" +
        pay_object["created_date"] +
        '</b></dd><dd style="font-size:18px;margin:4px 0">收款金额：<b>￥' +
        pay_object["amount"] +
        "元</b></dd><dd>￥" +
        this.intToChinese(pay_object["amount"]) +
        "</dd>";

      printTest +=
        '<dd style="font-size:12px;padding:6px;border:1px solid #ccc;margin:4px;text-align:left;">';
      printTest += "<p>" + pay_object["pay_detail"] + "</p><br>";
      printTest += "<p>备注:" + pay_object["remark"] + "</p>";
      printTest += "</dd>";

      if (pay_object["diff_amount"]) {
        printTest +=
          '<dd style="border-top:1px solid #333;margin:2px 0">未交金额：<b>￥' +
          pay_object["diff_amount"] +
          "元</b></dd>";
      } else {
        printTest +=
          '<dd style="border-top:1px solid #333;margin:2px 0"><b>已完成付款</b></dd>';
      }
      //        printTest += '</dl></div>';
      //        if (this.qrcode.is_show) {
      //        printTest += '<div style="text-align:center"><span >' + this.qrcode.tips  + '</span></div>';
      //
      //        printTest += '<div style="text-align:center"><img width="90%" src="' + this.qrcode.image_url +'"/></div>'
      //        }
      //        if (this.mini_app_qrcode.isShow){
      //          printTest += '<div style="text-align:center"><span >' + this.mini_app_qrcode.tips  + '</span></div>';
      //
      //          printTest += '<div style="text-align:center"><img width="50%" height="50%" src="' + this.mini_app_qrcode.image_url +'"/></div>'
      //        }
      return printTest;
    },
    // A4打印内容
    getA4PrintText(index){
      var printTest = "";
      printTest =
        '<div style="align-items:center;"><img style="vertical-align:middle" width="50" height="50" src="' +
        this.logo_url +
        '"/><span style="margin-left: 5px; font-weight:bold; font-size:20px" >' +
        this.org_name +
        "</span>";
      printTest +=
        '<img style="vertical-align:middle" width="80" height="80" src="' +
        this.qrcode_url +
        '"/>';
      printTest +=
        "<span margin-left: 5px; font-weight:bold; font-size:20px>" +
        this.qrcode_tip +
        '</span>    </div><dd style="border-top:1px solid #333;margin:2px 0">';

      printTest +=
        '<div style="  border-style:none;"><span style="font-size:20px"><b>学生：</b> ' +
        this.orderView.student_name +
        "</span>";

      if (this.orderView.school != "") {
        printTest +=
          '   <span style="margin-left:10px;font-size:20px"><b>学校：</b> ' +
          this.orderView.school +
          "</span>  ";
      }

      printTest +=
        '   <span style="margin-left:10px;font-size:20px"><b>校区：</b> ' +
        this.orderView.org_name +
        '</span></div><div><h1 style="text-align:left">课程明细：</h1>';
      printTest +=
        "<table><tr><th>课程</th><th>学期</th><th>开始日期</th><th>授课模式</th><th>数量</th><th>课时单价</th><th>原价学费</th><th>直减</th><th>折扣优惠</th><th>折后学费</th><th>教材费</th><th>小计学费</th></tr>";
      for (let i = 0; i < this.orderView.course_list.length; i++) {
        let course = this.orderView.course_list[i];
        let original_price =
          parseFloat(course.price) *
          parseFloat(course.times) *
          parseFloat(course.hours);
        let discount_price =
          parseFloat(course.reduce) + parseFloat(course.discount_amount);
        let str_discount = "";
        if (parseFloat(discount_price) != 0) {
          str_discount =
            "－优惠￥" +
            parseFloat(discount_price) +
            "元＝折后￥" +
            parseFloat(course.tuition_fees) +
            "元";
        }
        printTest +=
          "<tr><td>" +
          course.subject_name_print +
          "</td>"+
          "<td>" +
          parseFloat(course.hours) +
          "</td><td>" +
          course.times +
          "</td><td>" +
          parseFloat(course.price) +
          "元</td><td>" +
          parseFloat(original_price) +
          "元</td><td>" +
          parseFloat(course.reduce) +
          "元</td><td>" +
          parseFloat(course.discount) +
          "%</td><td>" +
          parseFloat(course.tuition_fees) +
          "元</td><td>" +
          parseFloat(course.sundry_fees) +
          "元</td><td>" +
          parseFloat(course.sub_total) +
          "元</td></tr>";
      }
      printTest += "</table>";
      let total_price =
        parseFloat(this.orderView.total_tuition_fees) +
        parseFloat(this.orderView.total_sundry_fees);
      //优惠金额为0时 不显示
      let str_other_discount = "";
      if (parseFloat(this.orderView.total_other_offers) != 0) {
        str_other_discount =
          " 其它费用：<b>￥" +
          parseFloat(this.orderView.total_other_offers) +
          "元</b> ";
      }
      printTest +=
        '<dl class="courselist" style="font-size:14px"><dd>合计学费：<b>￥<span>' +
        parseFloat(total_price) +
        "</span>元</b>    " +
        str_other_discount +
        "  应交金额：<b>￥" +
        parseFloat(this.orderView.receivable_total) +
        "元</b></dd>  </dl>";
      if (this.orderView.other_list.length) {
        printTest +=
          '<div style="font-weight:400;color:#333;text-align:left">（ 其它费用明细： ';
        for (let i = 0; i < this.orderView.other_list.length; i++) {
          let other = this.orderView.other_list[i];
          printTest += other.title + ":" + other.amount + "元 ";
        }
        printTest += "）</div>";
      }
      printTest += '</div><h1 style="text-align:left">收款明细：</h1>';
      let pay_count = 0;
      //收款记录
      let pay_object = new Array();
      index.sort(function(a, b) {
        return a - b;
      });
      printTest +=
        "<table><tr><th>应收学费</th><th>预收学费</th><th>差额</th><th>付款方式</th><th>收款日期</th><th>收款人</th><th>备注</th></tr>";
      for (var i of index) {
        let pay_detail = this.pay_map.get(i);
        console.log(pay_detail);
        if (pay_object["amount"] == null) {
          pay_object["amount"] = 0;
          pay_object["pay_detail"] = "";
        }
        pay_object["created_user"] = pay_detail.created_user;
        pay_object["created_date"] = DateFormat.formatDate(
          new Date(pay_detail.created_date * 1000),
          "yyyy-MM-dd"
        );

        pay_object["amount"] += parseFloat(pay_detail.amount);

        pay_object["pay_detail"] +=
          pay_detail.payment + ":" + pay_detail.amount + "元;";

        pay_object["remark"] = pay_detail.remark;
        pay_object["diff_amount"] = pay_detail.diff_amount;
        printTest +=
          "<tr>" +
          "<td>" +
          parseFloat(pay_detail.receivable_amount) +
          "</td>" +
          "<td>" +
          parseFloat(pay_detail.amount) +
          "</td>" +
          "<td>" +
          pay_detail.diff_amount +
          "</td>" +
          "<td>" +
          pay_detail.payment +
          "</td>" +
          "<td>" +
          DateFormat.formatDate(
            new Date(pay_detail.created_date * 1000),
            "yyyy-MM-dd"
          ) +
          "</td>" +
          "<td>" +
          pay_detail.created_user +
          "</td>" +
          "<td>" +
          pay_detail.remark +
          "</td>" +
          "</tr>";
      }
      printTest += "</table>";
      // for (var i of index) {
      //   pay_count ++;
      //  let   pay_detail = this.pay_map.get(i);
      //printTest += '<div id="selectPrint"><dl class="courselist" style="font-size:14px"><dd>收款人：<b>' + pay_object['created_user'] + '</b></dd><dd>收款时间：<b>'+ pay_object['created_date'] +'</b></dd><dd style="font-size:18px;margin:4px 0">收款金额：<b>￥'+ pay_object['amount'] +'元</b></dd><dd>￥'+ this.intToChinese((pay_object['amount'])) +'</dd>';
      printTest += "<div>";
      //printTest += '<dd style="font-size:12px;padding:6px;border:1px solid #ccc;margin:4px;text-align:left;">';
      //printTest += '<p>' + pay_object['pay_detail'] + '</p><br>';
      //printTest += '<p>备注:' + pay_object['remark'] + '</p>';
      //printTest += '</dd>';
      if (pay_object["diff_amount"]) {
        printTest +=
          '<dd style="border-top:1px solid #333;margin:2px 0">未交金额：<b>￥' +
          pay_object["diff_amount"] +
          "元</b></dd>";
      } else {
        printTest +=
          '<dd style="border-top:1px solid #333;margin:2px 0"><b>已完成付款</b></dd>';
      }
      printTest += "</dl></div>";
      return printTest;
    },
    /**
     * [createOneFormPage description]
     * @param  {[type]} id         [description]
     * @param  {[type]} printIndex [description]
     * @param  {[type]} print_sn   [description]
     * @return {[type]}            [description]
     */
    createOneFormPage: function(id, printIndex) {
      LODOP = Print.getLodop();
      LODOP.SET_PRINT_COPIES(1); //强制打印份数为1份
      LODOP.SET_LICENSES(
        "深圳市科翰教育科技有限公司",
        "EFB0D2938EE17DEF29294F4CA683CA27",
        "深圳市科翰教育科技有限公司",
        "0968ED96E99A737B332FD25ECA9B2CC9"
      );
      LODOP.SET_LICENSES(
        "THIRD LICENSE",
        "",
        "ShenZhen Kehan Education Technology Co. Ltd.",
        "931AB46B842EBE18377647E3F39BB9B6"
      );
      var strStyleCSS =
        "<style type='text/css'>.courselist {font-size:12px;margin-bottom:16px;border-top:1px solid #000;padding:4px;}.courselist > dd {text-align:right;padding:0;margin:0;}.courselist > dd > b {display:inline-block;width:120px;}ul.footer{font-size:12px;border-top:1px solid #000;padding: 8px 0;margin:0;list-style-type:none;}ul.footer li {padding:4px;}.largefont{font-size:18px;}.text-right{text-align:right} .text-center{text-align:center;} .text-left{text-align:left;} h1{font-size:18px;text-align:center;}div{font-size:9px;}  table,td,th { font-size:12px; border: 1 solid #000; /*border:0;*/border-collapse:collapse } table.noborder,table.noborder td,table.noborder th,.noborder,.noborder td,noborder th{border:0;} #print1 td{border-bottom:1px solid #000000;border-collapse:collapse} #print1,#print1 td,#print1 th  { border: 0; }  table{width:100%;margin-bottom:8px;} td,th{padding:4px;} th.text-center{text-align:center;} a{text-decoration:none;color:#333;} </style>";
      //            var strPrintTime = '<div class="text-center">打印时间：<b><u>'+ new Date().format('yyyy-MM-dd hh:mm:ss')+'</u></b> 制表人：<b><u>//</u></b> 打印人：<b><u>//</u></b></div>';
      var getTemplate = 1;
      var thisTemplate = "";
      switch (getTemplate) {
        case "1":
          thisTemplate = "print";
          break;
        case "2":
          thisTemplate = "printx";
          break;
        default:
          thisTemplate = "unkown";
      }
      //thisTemplate = "print";
      var strClientSignHtml =
        '<div style="font-size:16px;line-height:8em;text-align:left;padding:0 8px;font-weight: bold;">收款人签名：</div>';
      var strPrintTimeHtml =
        "<li>打印时间：<b><u>" +
        DateFormat.formatDate(new Date(), "yyyy-MM-dd hh:mm:ss") +
        "</u></b></li>";
      var strPrintToSomebodyHTML = "<li>第 {打印联数} 联，{给谁}</li>";
      var strPrintCreateByHTML = "<li>制表人：<b><u>admin</u></b></li>";
      var strPrintByHTML =
        "<li>打印人：<b><u>" + this.getUser.user_name + "</u></b></li>";
      var strHumanID =
        "<li>流水号：<b><u>" + this.print_log_sn + "</u></b></li>";
      thisTemplate = this.getPrintText(id);
      //console.log(strFormHtml);
      LODOP.PRINT_INIT("打印");
      // 名称：设定纸张大小
      // 格式：SET_PRINT_PAGESIZE(intOrient, PageWidth,PageHeight,strPageName)
      // intOrient 1---纵(正)向打印，固定纸张； 2---横向打印，固定纸张； 3---纵(正)向打印，宽度固定，高度按打印内容的高度自适应；0(或其它)----打印方向由操作者自行选择或按打印机缺省设置；
      LODOP.SET_PRINTER_INDEXA(this.PrintIndex);
      LODOP.SET_PRINT_PAGESIZE(1, "215mm", "140mm", "CreateCustomPage");
      LODOP.SET_PRINT_PAGESIZE(3, "80mm", "20mm", "");
      var strFormHtmlOut = "";
      for (var i = 1; i <= 2; i++) {
        LODOP.NewPage();
        switch (i) {
          case 1:
            strFormHtmlOut =
              strClientSignHtml +
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", i)
                .replace("{给谁}", "家长存根") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
          //                    case 2: strFormHtmlOut = '<ul class="footer">' + strPrintToSomebodyHTML.replace('{打印联数}',i).replace('{给谁}','财务存根') + strPrintTimeHtml  + strPrintByHTML+ strHumanID +'</ul>';break;
          case 2:
            strFormHtmlOut =
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", i)
                .replace("{给谁}", "分校存根") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
          default:
            strFormHtmlOut =
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", "X")
                .replace("{给谁}", "给XX") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
        }
        strFormHtmlOut =
          "<head>" +
          strStyleCSS +
          "</head>" +
          "<body>" +
          thisTemplate +
          strFormHtmlOut +
          "</body>";
        strFormHtmlOut = "<html>" + strFormHtmlOut + "</html>";
        //LODOP.ADD_PRINT_BARCODE("3mm","171mm","50mm","10mm","EAN128C","//");
        LODOP.ADD_PRINT_BARCODE(
          "3mm",
          "5mm",
          "70mm",
          "20mm",
          "EAN128B",
          this.orderView.order_sn
        );
        //LODOP.SET_PRINT_STYLEA(0,"ShowBarText",0);
        // 打印画面居中，会将此句以下的全部元素居中
        // SET_PRINT_STYLE(strStyleName,varStyleValue)
        // Alignment的值：数字型，1--左靠齐 2--居中 3--右靠齐，缺省值是1。
        // HOrient的值：数字型，0--左边距锁定 1--右边距锁定 2--水平方向居中 3--左边距和右边距同时锁定（中间拉伸），缺省值是0。
        // VOrient的值：数字型，0--上边距锁定 1--下边距锁定 2--垂直方向居中 3--上边距和下边距同时锁定（中间拉伸），缺省值是0。
        //LODOP.SET_PRINT_STYLE('HOrient','2');
      LODOP.ADD_PRINT_HTM("30mm", "0", "95%", "95%", strFormHtmlOut);
        //LODOP.ADD_PRINT_HTM("17mm","6mm","95%","95%",strFormHtml);
      }
      //SET_PREVIEW_WINDOW(intDispMode, intToolMode,blDirectPrint,inWidth,intHeight, strTitleButtonCaptoin)
      LODOP.SET_PREVIEW_WINDOW(1, 0, 0, 1024, 600, "asdfasdf-打印");

      if (LODOP.CVERSION) {
        this.$message("打印中，请稍候");
        //                let that = this;
        LODOP.On_Return = function(TaskID, Value) {
          console.log("打印回调Value:" + Value);
          if (Value == true) {
            this.$message.success("打印成功");
            console.log("打印成功", TaskID, LODOP);
            this.onPrintFinish(
              id,
              "[成功]",
              LODOP.GET_PRINTER_NAME(this.printIndex)
            );
            this.canclePrint();
            //                      this.logPrint();
          } else {
            this.$message.error("打印失败");
            console.log("error");
            this.onPrintFinish(
              id,
              "[失败:" + Value + "]",
              LODOP.GET_PRINTER_NAME(this.printIndex)
            );
          }
        }.bind(this);
      }
      LODOP.PRINT();
    },
    selectPrint(data) {
      this.PrintIndex = data;
    },
    // 1-->选择打印机
    getSelectedPrintIndex() {
      if (this.form.choose_print != "") return this.form.choose_print;
      else return -1;
    },
    //      logPrint(){
    //        console.log('打印地地道道的');
    //      },
    /**
     * [createOneFormPage description]
     * @param  {[type]} id         [description]
     * @param  {[type]} printIndex [description]
     * @param  {[type]} print_sn   [description]
     * @return {[type]}            [description]
     */
    // *****创建科翰打印
    createOneA4FormPage: function(id, printIndex) {
      LODOP = Print.getLodop();
      LODOP.SET_PRINT_COPIES(1); //强制打印份数为1份
      LODOP.SET_LICENSES(
        "深圳市科翰教育科技有限公司",
        "EFB0D2938EE17DEF29294F4CA683CA27",
        "深圳市科翰教育科技有限公司",
        "0968ED96E99A737B332FD25ECA9B2CC9"
      );
      LODOP.SET_LICENSES(
        "THIRD LICENSE",
        "",
        "ShenZhen Kehan Education Technology Co. Ltd.",
        "931AB46B842EBE18377647E3F39BB9B6"
      );
      var strStyleCSS =
        "<style type='text/css'>.courselist {font-size:12px;margin-bottom:16px;border-top:1px solid #000;padding:4px;}.courselist > dd {text-align:right;padding:0;margin:0;}.courselist > dd > b {display:inline-block;width:120px;}ul.footer{font-size:12px;border-top:1px solid #000;padding: 8px 0;margin:0;list-style-type:none;}ul.footer li {padding:4px;}.largefont{font-size:18px;}.text-right{text-align:right} .text-center{text-align:center;} .text-left{text-align:left;} h1{font-size:18px;text-align:center;}div{font-size:9px;}  table,td,th { font-size:12px; border: 1 solid #000; /*border:0;*/border-collapse:collapse } table.noborder,table.noborder td,table.noborder th,.noborder,.noborder td,noborder th{border:0;} #print1 td{border-bottom:1px solid #000000;border-collapse:collapse} #print1,#print1 td,#print1 th  { border: 0; }  table{width:100%;margin-bottom:8px;} td,th{padding:4px;} th.text-center{text-align:center;} a{text-decoration:none;color:#333;} </style>";
      //            var strPrintTime = '<div class="text-center">打印时间：<b><u>'+ new Date().format('yyyy-MM-dd hh:mm:ss')+'</u></b> 制表人：<b><u>//</u></b> 打印人：<b><u>//</u></b></div>';
      var getTemplate = 1;
      var thisTemplate = "";
      switch (getTemplate) {
        case "1":
          thisTemplate = "print";
          break;
        case "2":
          thisTemplate = "printx";
          break;
        default:
          thisTemplate = "unkown";
      }
      //thisTemplate = "print";
      var strClientSignHtml =
        '<div style="font-size:16px;line-height:8em;text-align:left;padding:0 8px;font-weight: bold;">收款人签名：</div>';
      var strPrintToSomebodyHTML = "<li>第 {打印联数} 联，{给谁}</li>";
      var strPrintTimeHtml =
        "<li>打印时间：<b><u>" +
        DateFormat.formatDate(new Date(), "yyyy-MM-dd hh:mm:ss") +
        "</u></b>   ";
      var strPrintCreateByHTML = "  制表人：<b><u>admin</u></b>  ";
      var strPrintByHTML =
        "   打印人：<b><u>" + this.getUser.user_name + "</u></b> ";
      var strHumanID =
        "   流水号：<b><u>" + this.print_log_sn + "</u></b></li>";
      thisTemplate = this.getA4PrintText(id);
      //console.log(strFormHtml);
      LODOP.PRINT_INIT("打印");
      // 名称：设定纸张大小
      // 格式：SET_PRINT_PAGESIZE(intOrient, PageWidth,PageHeight,strPageName)
      // intOrient 1---纵(正)向打印，固定纸张； 2---横向打印，固定纸张； 3---纵(正)向打印，宽度固定，高度按打印内容的高度自适应；0(或其它)----打印方向由操作者自行选择或按打印机缺省设置；
      LODOP.SET_PRINTER_INDEX(this.PrintIndex);
      LODOP.SET_PRINT_PAGESIZE(2, "210mm", "297mm", "CreateCustomPage");
      //LODOP.SET_PRINT_PAGESIZE(3,"80mm","20mm","");
      var strFormHtmlOut = "";
      for (var i = 1; i <= 2; i++) {
        LODOP.NewPage();
        switch (i) {
          case 1:
            strFormHtmlOut =
              strClientSignHtml +
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", i)
                .replace("{给谁}", "家长存根") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
          //                    case 2: strFormHtmlOut = '<ul class="footer">' + strPrintToSomebodyHTML.replace('{打印联数}',i).replace('{给谁}','财务存根') + strPrintTimeHtml  + strPrintByHTML+ strHumanID +'</ul>';break;
          case 2:
            strFormHtmlOut =
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", i)
                .replace("{给谁}", "分校存根") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
          default:
            strFormHtmlOut =
              '<ul class="footer">' +
              strPrintToSomebodyHTML
                .replace("{打印联数}", "X")
                .replace("{给谁}", "给XX") +
              strPrintTimeHtml +
              strPrintByHTML +
              strHumanID +
              "</ul>";
            break;
        }
        strFormHtmlOut =
          "<head>" +
          strStyleCSS +
          "</head>" +
          "<body>" +
          thisTemplate +
          strFormHtmlOut +
          "</body>";
        strFormHtmlOut = "<html>" + strFormHtmlOut + "</html>";

        //LODOP.ADD_PRINT_BARCODE("3mm","171mm","50mm","10mm","EAN128C","//");
        LODOP.ADD_PRINT_BARCODE(
          "3mm",
          "200mm",
          "60mm",
          "10mm",
          "EAN128B",
          this.orderView.order_sn
        );
        //LODOP.SET_PRINT_STYLEA(0,"ShowBarText",0);
        // 打印画面居中，会将此句以下的全部元素居中
        // SET_PRINT_STYLE(strStyleName,varStyleValue)
        // Alignment的值：数字型，1--左靠齐 2--居中 3--右靠齐，缺省值是1。
        // HOrient的值：数字型，0--左边距锁定 1--右边距锁定 2--水平方向居中 3--左边距和右边距同时锁定（中间拉伸），缺省值是0。
        // VOrient的值：数字型，0--上边距锁定 1--下边距锁定 2--垂直方向居中 3--上边距和下边距同时锁定（中间拉伸），缺省值是0。
        //            LODOP.SET_PRINT_STYLE('HOrient','2');
        LODOP.ADD_PRINT_HTM("3mm", "0", "95%", "95%", strFormHtmlOut);
        //            LODOP.ADD_PRINT_HTM("17mm","6mm","95%","95%",strFormHtml);
      }
      //SET_PREVIEW_WINDOW(intDispMode, intToolMode,blDirectPrint,inWidth,intHeight, strTitleButtonCaptoin)
      LODOP.SET_PREVIEW_WINDOW(1, 0, 0, 1024, 600, "asdfasdf-打印");
      if (LODOP.CVERSION) {
        this.$message("打印中，请稍候");
        LODOP.On_Return = function(TaskID, Value) {
          console.log("打印回调Value:" + Value);
          if (Value == true) {
            this.$message.success("打印成功");
            this.onA4PrintFinish(
              id,
              "[成功][A4]",
              LODOP.GET_PRINTER_NAME(printIndex)
            );
          } else {
            this.$message.error("打印失败");
            this.onA4PrintFinish(
              id,
              "[失败:" + Value + "][A4]",
              LODOP.GET_PRINTER_NAME(printIndex)
            );
          }
        }.bind(this);
      }
    },
    /**
     * 打印完成回调
     * @param  {[type]} index        [description]
     * @param  {[type]} result_hint  [description]
     * @param  {[type]} printer_name [description]
     * @return {[type]}              [description]
     */
    onPrintFinish(index, result_hint, printer_name) {
      let api_url = "";
      console.log("index", index);
      if (index.length == 1) {
        api_url = "printCreate";
      } else {
        api_url = "printBatchCreate";
      }
      console.log("请求打印接口");
      console.log(index);
      console.log(api_url);
      let p_remark = result_hint + this.print_remark;
      let temp_ids = new Array();
      for (var i = 0; i < index.length; i++) {
        if (!this.isEmpty(index[i])) {
          temp_ids.push(index[i]);
        }
      }
      batchPrintCreate(
        this.getPrintText(index),
        temp_ids[0],
        JSON.stringify(temp_ids),
        printer_name,
        p_remark,
        this.print_log_sn
      )
        .then(res => {
          this.print_remark = "";
          this.print_log_sn = "";
          this.init();
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    // *require 金额大小写
    intToChinese(n) {
      if (!/^(0|[1-9]\d*)(\.\d+)?$/.test(n)) return "数据非法";
      var unit = "千百拾亿千百拾万千百拾元角分",
        str = "";
      n += "00";
      var p = n.indexOf(".");
      if (p >= 0) n = n.substring(0, p) + n.substr(p + 1, 2);
      unit = unit.substr(unit.length - n.length);
      for (var i = 0; i < n.length; i++)
        str += "零壹贰叁肆伍陆柒捌玖".charAt(n.charAt(i)) + unit.charAt(i);
      return str
        .replace(/零(千|百|拾|角)/g, "零")
        .replace(/(零)+/g, "零")
        .replace(/零(万|亿|元)/g, "$1")
        .replace(/(亿)万|壹(拾)/g, "$1$2")
        .replace(/^元零?|零分/g, "")
        .replace(/元$/g, "元整");
    },
    //选择打印
    choose_print(pay_ids) {
      this.printLogDialogVisible = false; //打印纪录对话框
      this.printLogDetailDialogVisible = false; //打印详情对话框
      this.printAlertDialogVisible = false; //补打原因对话框
      this.multiPrintAlertDialogVisible = false;
      this.printA4AlertDialogVisible = false;
      this.multiA4PrintAlertDialogVisible = false;
      this.print_log_sn = this.randomString(6);
      this.LODOP = Print.getLodop();
      var status = this.LODOP.SELECT_PRINTER();
      var vm = this;
      if (LODOP.CVERSION) {
        LODOP.On_Return = function(TaskID, Value) {
          console.log("printIndex:" + Value + ";TaskID" + TaskID);
          if (Value == -1) open_type = 0;
          if (Value > -1) {
            vm.createOneFormPage(pay_ids, Value);
            LODOP.PRINT();
          }
          // ajax 写入打印次数、打印时间、打印人、打印订单；
          // 修改全局打印次数+=value；
        }.bind(this);
      }
    },
    closePrintList() {
      this.showPrintList = false;
    },
    // ————————————————————————————————————老打印分割线————————————————————————————————————————
    // 易联云打印
    newPrint(){
      let index = this.pay_select;
      if (index.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }
      let total_price =
        parseFloat(this.orderView.total_tuition_fees) +
        parseFloat(this.orderView.total_sundry_fees);
      let content = "";
        content +="<BR2>"+this.orderInfo.order_sn+"</BR2>\r";
        content += "<FS>校区:"+this.orderView.org_name+"</FS>\r\r";
          // content += "______________________________________________\r";
          // content +="<FS2><center>--在线支付--</center></FS2>";
        content +="<FS>学生:"+this.orderView.student_name+"</FS>\r\r";
        // content +="订单时间:"+DateFormat.formatDate(new Date(), "yyyy-MM-dd hh:mm:ss")+"\n";
        content +="<table>";
        content +="<tr><td>           课程费</td><td>优惠</td><td>小计\n</td></tr>";
        // <td>教材费</td>
        for (let i = 0; i < this.orderView.course_list.length; i++) {
        let course = this.orderView.course_list[i];
        let original_price =parseFloat(course.price) *parseFloat(course.times) *parseFloat(course.hours);
        let discount_price =parseFloat(course.reduce) + parseFloat(course.discount_amount);
        let str_discount = "";
        if (parseFloat(discount_price) != 0) {
          str_discount ="－优惠￥" +parseFloat(discount_price) +"元＝折后￥" +parseFloat(course.tuition_fees) +"元";
        }
        if (
          course.sundry_fees != null &&
          course.sundry_fees != "" &&
          course.sundry_fees != 0 &&
          course.sundry_fees
        ) {
          content +="<tr><td>课程名称:"+course.subject_name_print+"(共"+(course.attend_type == 1? Number(course.hours)*course.times:course.times)+"课时)\n</td></tr>";
          if(parseFloat(discount_price) != 0){
            content +="<tr><td>"+"原价¥"+parseFloat(original_price)+"元"+str_discount+"</td></tr>"
          }
          content +="<tr><td>           "+parseFloat(original_price) +"元</td>";
          // content +="<td>"+parseFloat(course.sundry_fees)+"元</td>";
          content +="<td>"+parseFloat(discount_price)+"</td>";
          content +="<td>"+course.sub_total+"</td></tr>";
          content += "<tr><td>教材费:           "+parseFloat(course.sundry_fees)+"元</td></tr>"
        } else {
          content +="<tr><td>课程名称:"+course.subject_name_print+"(共"+(course.attend_type == 1? Number(course.hours)*course.times:course.times)+"课时)\n</td></tr>";
          // +course.times+"次)\n</td></tr>";
          if(parseFloat(discount_price) != 0){             
            content +="<tr><td>"+"原价¥"+parseFloat(original_price)+"元"+str_discount+"</td></tr>"           
          }
          content +="<tr><td>          "+parseFloat(original_price) +"元</td>"
          // content +="<td>0元</td>"
          content +="<td>"+parseFloat(discount_price)+"</td>";
          content +="<td>"+course.sub_total+"</td></tr>"
        }
        // content +="<tr><td>单科优惠:"+parseFloat(discount_price)+"</td></tr>";
        // content +="<tr><td>单科合计:"+course.sub_total+"</td></tr>";
        content +="<tr><td>______________________________________________\r</td></tr>";
      }
        content +="</table>"; 
        content +="<right>学费合计:"+parseFloat(total_price)+"元</right>\r\r";
        content +="<right>应交金额:"+parseFloat(this.orderView.receivable_total)+"元</right>\r\r";
      // 收款记录
      let pay_object = new Array();
      index.sort(function(a, b) {
        return a - b;
      });
      for (var i of index) {
        console.log("执行:" + i);
        if (this.isEmpty(i)) {
          continue;
        }
        let pay_detail = this.pay_map.get(i);
        console.log(pay_detail);
        if (pay_object["amount"] == null) {
          pay_object["amount"] = 0;
          pay_object["pay_detail"] = "";
        } else {
          console.log('前',pay_object['amount'])
          pay_object['amount'] = Number(pay_object['amount'].toString().match(/^\d+(?:\.\d{0,2})?/))
          console.log('后',pay_object['amount'])
        }
        pay_object["created_user"] = pay_detail.created_user;
        pay_object["created_date"] = DateFormat.formatDate(
          new Date(pay_detail.created_date * 1000),
          "yyyy-MM-dd"
        );
        //          console.log('pay_detail.amount',pay_detail.amount, pay_object['amount']);
        pay_object["amount"] =
          Number(pay_object["amount"]) + Number(pay_detail.amount);
        pay_object["amount"] = pay_object["amount"].toFixed(2);
        pay_object["pay_detail"] +=
          pay_detail.payment + ":" + pay_detail.amount + "元;";
        pay_object["remark"] = pay_detail.remark;
        pay_object["diff_amount"] = Number(pay_detail.diff_amount).toFixed(2);
      }
          // content +="______________________________________________\r";
          content +="<FS>收款方式:"+pay_object["pay_detail"]+"</FS>\r\r";
          content +="<FS>收款金额:"+pay_object["amount"]+"("+this.intToChinese(pay_object["amount"])+")</FS>\r\r";
          content +="<FS>未交金额:"+pay_object["diff_amount"]+ "</FS>\r\r";
          // content +="大写:"+this.intToChinese(pay_object["amount"])+" \n";
          content +="<right>收款人:"+pay_object["created_user"]+"</right>\r\r";
          content +="<right>收款时间:"+pay_object["created_date"]+"</right>\r\r";
          content +="<right>打印人:"+this.getUser.user_name+"</right>\r\r";
          content +="<right>打印时间:"+DateFormat.formatDate(new Date(),"yyyy-MM-dd hh:mm:ss")+"</right>\r\r"
          content +="<right>流水号:"+this.print_log_sn+"</right>\r\r"
          content +="<QR>http://weixin.qq.com/r/xhw-JxfEY0ocrVNE90nU</QR>";
          content +="\r\r<center>扫码获取家校沟通操作指南</center>"
          // content +="______________________________________________\r";
          // content +="<FS><FB><center>感谢您对科翰教育的支持</center></FB></FS>";
      let obj = {
        content:content,
        payin_id:JSON.stringify(index)
      }    
      this.fullLoading = true;
      console.log(this.pay_map)
      postPrint(obj).then(res => {
        console.log(res);
        this.fullLoading = false;
        this.$message.success("打印成功");
        this.getOrderDetail();
      }).catch(error => {
        this.$message.error(error);
        this.fullLoading = false;
      });
    },
    newPrintK4(){
      let index = this.pay_select;
      if (index.length == 0) {
        this.$message.error("请选择需要打印的记录");
        return false;
      }
      let total_price =
        parseFloat(this.orderView.total_tuition_fees) +
        parseFloat(this.orderView.total_sundry_fees);
      let content = "";
        content +="<BR2>"+this.orderInfo.order_sn+"</BR2>\r";
        content += "<FS>校区:"+this.orderView.org_name+"</FS>\r\r";
          // content += "______________________________________________\r";
          // content +="<FS2><center>--在线支付--</center></FS2>";
        content +="<FS>学生:"+this.orderView.student_name+"</FS>\r\r";
        // content +="订单时间:"+DateFormat.formatDate(new Date(), "yyyy-MM-dd hh:mm:ss")+"\n";
        content +="<table>";
        content +="<tr><td>      课程费</td><td>优惠</td><td>小计\n</td></tr>";
        // <td>教材费</td>
        for (let i = 0; i < this.orderView.course_list.length; i++) {
        let course = this.orderView.course_list[i];
        let original_price =parseFloat(course.price) *parseFloat(course.times) *parseFloat(course.hours);
        let discount_price =parseFloat(course.reduce) + parseFloat(course.discount_amount);
        let str_discount = "";
        if (parseFloat(discount_price) != 0) {
          str_discount ="－优惠￥" +parseFloat(discount_price) +"元＝折后￥" +parseFloat(course.tuition_fees) +"元";
        }
        if (
          course.sundry_fees != null &&
          course.sundry_fees != "" &&
          course.sundry_fees != 0 &&
          course.sundry_fees
        ) {
          content +="<tr><td>课程名称:"+course.subject_name_print+"(共"+(course.attend_type == 1? Number(course.hours)*course.times:course.times)+"次)\n</td></tr>";
          if(parseFloat(discount_price) != 0){             
            content +="<tr><td>"+"原价¥"+parseFloat(original_price)+"元"+str_discount+"</td></tr>"           
          }

          content +="<tr><td>      "+parseFloat(original_price) +"元</td>";
          // content +="<td>"+parseFloat(course.sundry_fees)+"元</td>";
          content +="<td>"+parseFloat(discount_price)+"</td>";
          content +="<td>"+course.sub_total+"</td></tr>";
          content += "<tr><td>教材费:        "+parseFloat(course.sundry_fees)+"元</td></tr>"
        } else {
          content +="<tr><td>课程名称:"+course.subject_name_print+"(共"+(course.attend_type == 1? Number(course.hours)*course.times:course.times)+"次)\n</td></tr>";
          if(parseFloat(discount_price) != 0){             
            content +="<tr><td>"+"原价¥"+parseFloat(original_price)+"元"+str_discount+"</td></tr>"           
          }
          content +="<tr><td>          "+parseFloat(original_price) +"元</td>"
          // content +="<td>0元</td>"
          content +="<td>"+parseFloat(discount_price)+"</td>";
          content +="<td>"+course.sub_total+"</td></tr>"
        }
        // content +="<tr><td>单科优惠:"+parseFloat(discount_price)+"</td></tr>";
        // content +="<tr><td>单科合计:"+course.sub_total+"</td></tr>";
        content +="<tr><td>____________________________</td></tr>";
      }
        content +="</table>"; 
        content +="<right>学费合计:"+parseFloat(total_price)+"元</right>\r";
        content +="<right>应交金额:"+parseFloat(this.orderView.receivable_total)+"元</right>\r";
      // 收款记录
      let pay_object = new Array();
      index.sort(function(a, b) {
        return a - b;
      });
      for (var i of index) {
        console.log("执行:" + i);
        if (this.isEmpty(i)) {
          continue;
        }
        let pay_detail = this.pay_map.get(i);
        console.log(pay_detail);
        if (pay_object["amount"] == null) {
          pay_object["amount"] = 0;
          pay_object["pay_detail"] = "";
        } else {
          console.log('前',pay_object['amount'])
          pay_object['amount'] = Number(pay_object['amount'].toString().match(/^\d+(?:\.\d{0,2})?/))
          console.log('后',pay_object['amount'])
        }
        pay_object["created_user"] = pay_detail.created_user;
        pay_object["created_date"] = DateFormat.formatDate(
          new Date(pay_detail.created_date * 1000),
          "yyyy-MM-dd"
        );
        //          console.log('pay_detail.amount',pay_detail.amount, pay_object['amount']);
        pay_object["amount"] =
          Number(pay_object["amount"]) + Number(pay_detail.amount);
        pay_object["amount"] = pay_object["amount"].toFixed(2);
        pay_object["pay_detail"] +=
          pay_detail.payment + ":" + pay_detail.amount + "元;";
        pay_object["remark"] = pay_detail.remark;
        pay_object["diff_amount"] = Number(pay_detail.diff_amount).toFixed(2);
      }
          // content +="______________________________________________\r";
          content +="<FS>收款方式:"+pay_object["pay_detail"]+"</FS>\r";
          content +="<FS>收款金额:"+pay_object["amount"]+"("+this.intToChinese(pay_object["amount"])+")</FS>\r";
          content +="<FS>未交金额:"+pay_object["diff_amount"]+ "</FS>\r";
          // content +="大写:"+this.intToChinese(pay_object["amount"])+" \n";
          content +="<right>收款人:"+pay_object["created_user"]+"</right>\r";
          content +="<right>收款时间:"+pay_object["created_date"]+"</right>\r";
          content +="<right>打印人:"+this.getUser.user_name+"</right>\r";
          content +="<right>打印时间:"+DateFormat.formatDate(new Date(),"yyyy-MM-dd hh:mm:ss")+"</right>\r"
          content +="<right>流水号:"+this.print_log_sn+"</right>\r"
          content +="<QR>http://weixin.qq.com/r/xhw-JxfEY0ocrVNE90nU</QR>";
          content +="\r\r<center>扫码获取家校沟通操作指南</center>"
          // content +="______________________________________________\r";
      let obj = {
        content:content,
        payin_id:JSON.stringify(index)
      }    
      this.fullLoading = true;
      console.log(this.pay_map)
      postPrint(obj).then(res => {
        console.log(res);
        this.fullLoading = false;
        this.$message.success("打印成功");
        this.getOrderDetail();
      }).catch(error => {
        this.$message.error(error);
        this.fullLoading = false;
      });
    }
  },
  computed: {
    ...mapState({
      getUser: state => state.user,
    }),
    ...mapGetters(['orderDetailsRefresh']),
    payStatus() {
      if (this.orderInfo && this.orderInfo.received_total/1 == 0) {
        return false;
      } else {
        return true;
      }
    },
  },
  watch:{
    orderDetailsRefresh(val){
      if(val === true){
        this.getOrderDetail();
        this.$store.commit("setOrderDetailRefresh",false);
      }
    }
  },
  mounted() {
    this.init();
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.student-order-details
  padding-top: 20px;
  min-height: 600px;
  .title_wrap
    height: 55px;
    line-height: 55px;
    border-bottom: 1px solid #ebebeb;
    .title
      padding-left: 30px;
    .item
      border-radius: 50% !important;
      padding: 0 3px !important;
      background: #bbbbbb;
      color: #ffffff;
  .pub-title
    position: relative;
    padding-left: 23px;
    background: #f7f7f7;
    font-size: 16px;
    line-height: 40px;
    .to-download
      font-size: 14px;
      position: absolute;
      right: 30px;
      top: 50%;
      color: #409EFF;
      transform: translateY(-50%);
      &:hover
        color: #999;
  .student-info-wrap
    margin: 0 20px;
    .student-info
      margin-top: 20px;
      margin-bottom: 20px;
      .header-bar
        text-align: center;
        font-size: 14px;
        .el-col
          line-height: 40px;
          border: 1px solid #ebebeb;
          border-bottom: none;
      .input-bar
        .el-col
          border: 1px solid #ebebeb;
          font-size: 14px;
          line-height: 40px;
          text-align: center;
  .other-fee
    margin: 0 20px;
    .tips-text
      display: inline-block;
      color: #8690ac;
      i
        margin: 0 5px 0 15px ;
    .add-btn
      margin-top: 20px;
    .other-fee-list
      margin-top: 20px;
      .el-row
        margin-bottom: 10px;
        .el-col
          margin-right: 20px;
        .tip
          align-self: center;
          color: #999;
    .other-fee-submit
      margin-top: 20px;
      margin-bottom: 20px;
  .pay-list-wrap
    margin: 0 20px;
    .pay-show-bar
      padding: 10px 0;
      line-height: 30px;
      border-bottom: 1px solid #ebebeb;
    .pay-list
      padding-left: 23px;
    .button-add
      height: 49px;
      line-height: 49px;
      background: #F7F7F7;
      border: 1px solid #ebebeb;
      border-top: none;
      text-align: center;
    .pay-add-wrap
      margin-left: 23px;
      margin-top: 20px;
      margin-bottom: 20px;
      .el-col
        margin-right: 10px;
.select-teacher
  display: inline-block;
</style>
