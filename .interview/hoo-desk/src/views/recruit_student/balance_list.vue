<template>
  <div class="close-wrap">
    <div class='close-bg'
         @click.stop.prevent='close'></div>
    <div class="content-box"
         v-show="!withdrawFormShow">
      <div class="title-bar">
        <div class="name">钱包余额-{{balanceUser.student_name}}</div>
        <div class="close"
             @click.stop.prevent='close'>
          <i class="hoo hoo-close"></i>
        </div>
      </div>
      <div class="wrap-box">
        <p>钱包余额 (元)</p>
        <p class="num">{{totalBalance}}</p>
        <el-button @click='withdrawFormShow = true'>立即提现</el-button>
      </div>
      <div class="table-top-bar">
        收支记录
      </div>
      <ul class="balance-list"
          v-if="listData.length != 0">
        <li :class="['list-item',item.order_sn ? 'can-nav':'']"
            @click="toOrder(item)"
            v-for="(item) in listData"
            :key="item.created_date">
          <div class="left">
            <div class="type">{{item.type}}</div>
            <div class="order_number"
                 v-if="item.order_sn">订单号：{{item.order_sn}}</div>
          </div>
          <div class="right">
            <div :class="['num',item.mode === '+' ? '':'minus']">{{item.mode}} {{item.money}} 元</div>
            <div class='status'>{{item.status}}</div>
            <div class="time">{{item.created_date|formatToDate}}</div>
          </div>
        </li>
      </ul>
      <!-- <el-row v-if="listData.length != 0"
              class='balance-list'
              type='flex'>
        <el-row class='balance-item'
                type='flex'
                v-for="(item) in listData"
                :key="item.created_date">
          <el-row type='flex'>
            <el-col :span='16'
                    class='text'>
              {{item.type}}
            </el-col>
            <el-col :span='7'
                    :offset="1"
                    class='num'>{{item.mode}} {{item.money}}元</el-col>
          </el-row>
          <el-row type='flex'>
            <el-col :span='24'
                    class='time'>{{item.created_date|formatToDate}}</el-col>
          </el-row>
        </el-row>
      </el-row> -->
      <p class='no-result'
         v-else>暂无记录</p>
    </div>
    <el-dialog class='withdrawForm'
               width='500px'
               @close="widthrawFormClose"
               title="申请提现"
               :visible.sync="withdrawFormShow"
               :modal="false">
      <el-form :model="withdrawFormData"
               ref="withdrawForm"
               :rules="formRules">
        <el-form-item label="提现金额"
                      prop="pay_money">
          <el-input v-model="withdrawFormData.pay_money"
                    placeholder="请输入提现金额"></el-input>
        </el-form-item>
        <el-form-item label="收款人"
                      prop="card_holder">
          <el-input v-model="withdrawFormData.card_holder"
                    placeholder="请输入收款人"></el-input>
        </el-form-item>
        <el-form-item label="收款银行"
                      prop="bank_name">
          <el-input v-model="withdrawFormData.bank_name"
                    placeholder="请输入收款银行"></el-input>
        </el-form-item>
        <el-form-item label="银行账户"
                      prop="card_number">
          <el-input v-model="withdrawFormData.card_number"
                    placeholder="请输入银行账户"></el-input>
        </el-form-item>
        <el-form-item label="备注"
                      prop="remark">
          <el-input v-model="withdrawFormData.remark"
                    placeholder="请输入备注"></el-input>
        </el-form-item>
      </el-form>
      <div class="btn-bar">
        <el-button @click="withdrawFormShow = false">取消</el-button>
        <el-button @click="submit"
                   type='primary'>提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import { getBalanceList, toWithdraw } from "@/api/balance";
export default {
  props: {
    balanceUser: Object
  },
  data() {
    return {
      listData: [],
      totalBalance: 0,
      withdrawFormShow: false,
      withdrawFormData: {
        card_holder: "",
        bank_name: "",
        card_number: "",
        pay_money: "",
        remark: ""//备注
      },
      formRules: {
        pay_money: [
          {
            required: true,
            message: "请输入提现金额",
            trigger: "blur"
          }
        ],
        // card_holder: [
        //   {
        //     required: true,
        //     message: "请输入收款人",
        //     trigger: "blur"
        //   }
        // ],
        // bank_name: [
        //   {
        //     required: true,
        //     message: "请输入收款银行",
        //     trigger: "blur"
        //   }
        // ],
        // card_number: [
        //   {
        //     required: true,
        //     message: "请输入银行账户",
        //     trigger: "blur"
        //   }
        // ]
      },
      isRefresh: false //学员管理是否需要刷新
    };
  },
  created() {
    this.getList();
  },
  methods: {
    close() {
      this.$emit("closeBalanceList", this.isRefresh);
    },
    getList() {
      getBalanceList({ student_id: this.balanceUser.student_id })
        .then(res => {
          this.listData = res.data.list;
          this.totalBalance = res.data.total_balance;
        })
        .catch(e => console.log(e));
    },
    //提现表单关闭
    widthrawFormClose() {
      this.$refs["withdrawForm"].resetFields();
    },
    //提交
    submit() {
      if (this.withdrawFormData.pay_money - this.totalBalance > 0) {
        this.$message.error("提现金额超出。");
        return;
      }
      this.$refs.withdrawForm
        .validate()
        .then(() => {
          let params = Object.assign(this.withdrawFormData, {
            student_id: this.balanceUser.student_id
          });
          return toWithdraw(params);
        })
        .then(res => {
          this.$message.success(res.msgs);
          this.withdrawFormShow = false;
          this.isRefresh = true;
          this.getList();
        })
        .catch(e => {
          console.log(e);
          if (e !== false) {
            this.$message.error(e);
          }
        });
    },
    toOrder(item) {
      if (item.order_sn) {
        this.$router.push({
          name: "order_detail_new",
          query: { order_id: item.order_id }
        });
      }
    }
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.close-wrap
  position: fixed;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 97;
  .close-bg
    position: fixed;
    z-index: 98;
    top: 0;
    left: 0;
    background: rgba(0, 0, 0, 0.7);
    width: 100%;
    height: 100%;
    overflow: hidden;
  .content-box
    position: absolute;
    z-index: 99;
    left: 50%;
    top: 50%;
    transform: translateX(-50%) translateY(-50%);
    width: 500px;
    height: 650px;
    border-radius: 4px;
    overflow: hidden;
    background: #fff;
    .title-bar
      line-height: 60px;
      display: flex;
      height: 60px;
      box-sizing: border-box;
      justify-content: space-between;
      padding: 0 20px;
      border-bottom: 1px solid #eee;
      .name
        font-size: 20px;
        color: #000;
    .wrap-box
      height: 190px;
      border-bottom: 1px solid #eee;
      box-sizing: border-box;
      text-align: center;
      padding-top: 28px;
      p
        font-size: 14px;
        color: #999;
        line-height: 36px;
      .num
        font-size: 32px;
        color: #000;
        line-height: 36px;
      .el-button
        margin-top: 14px;
        border: 1px solid #409eff;
        background: #fff;
        color: #409eff;
        &:hover
          opacity: 0.8;
    .table-top-bar
      height: 40px;
      border-bottom: 1px solid #eee;
      box-sizing: border-box;
      padding-left: 19px;
      color: #999;
      font-size: 14px;
      line-height: 40px;
    .balance-list
      height: calc(100% - 40px - 190px - 60px);
      overflow-y: auto;
      .list-item
        display: flex;
        padding: 10px 20px;
        &.can-nav
          cursor: pointer;
          &:hover
            background-color: #f2f7f9;
        .left
          display: flex;
          flex: 1;
          flex-direction: column;
          justify-content: space-between;
          .order_number
            font-size: 12px;
            color: #999;
        .right
          display: flex;
          flex-direction: column;
          text-align: right;
          flex: 0 0 auto;
          justify-content: space-between;
          .num
            color: #e51c23;
            font-size: 18px;
            &.minus
              color: #999;
          .status
            color:#333;
            font-size: 16px;
          .time
            font-size: 14px;
            color: #333;
        &:nth-child(2n)
          background: #f5f7fa;
    .no-result
      margin-top: 50px;
      font-size: 16px;
      text-align: center;
  .withdrawForm
    .btn-bar
      padding-right: 20px;
      line-height: 70px;
      height: 70px;
      border-top: 1px solid #eee;
      justify-content: flex-end;
      display: flex;
      .el-button
        width: 120px;
        height: 40px;
        align-self: center;
</style>