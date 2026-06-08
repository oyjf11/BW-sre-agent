<template>
  <div>
    <v-tag-bar :tagList="tagsArr" @change="typeChange"></v-tag-bar>
    <v-table-wrap
      :page="page"
      :total="count"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      v-if="pageType === 0">
      <template slot="searchItems">
        <v-radio-bar
          :radio="is_new"
          :all="false"
          label="结算类型"
          @onChange="filterChange($event,'is_new')"
          :radioList="listType"
        ></v-radio-bar>
        <el-popover
          @show="showAccountDetails"
          v-model="accountShow"
          placement="right"
          width="400"
          trigger="click"
        >
          <div class="account-details" v-loading='accountLoading' v-if="detailList.length !== 0">
            <div
              class="details-row"
              v-show="item.show"
              v-for="(item,index) in detailList"
              :key="index"
            >
              <div class="label">{{item.label}}</div>
              <div class="data">{{item.data}}</div>
            </div>
            <div class="tips-content">请详细查验以上结算信息，确认申请结算后无法撤回，且已结算的订单系统将无法自动退款(只能由老师手动退款)</div>
            <el-button type="primary" @click="submitOrder" class="submit-btn">确认</el-button>
          </div>
          <div v-else>{{toAccountText}}</div>
          <el-button type="primary" slot="reference">生成结算订单</el-button>
        </el-popover>
        <p class="tips-text">
          <span v-if="pageType===0">结算中和结算后的订单无法继续在线退款
            <br>
          </span>
          <span>红包拼课活动需要在活动结束后才能进行结算</span>
          <br>
          <span>对公账户提现小云翰平台不收取任何手续费，仅微信官方收取0.6%，若对私账户或微信零钱包则收取额外3%的税务费用</span>
          <br>
          <span>满100的申请才会进行结算，不满100元的申请会连同下一批次统一结算</span>
        </p>
      </template>
      <template slot='table_title'>结算列表</template>
      <el-table slot="table"  v-show="pageType ===0" class="pub-table" :data="listData" v-loading="listLoading">
        <el-table-column label="序号" type="index"></el-table-column>
        <el-table-column label="结算订单号" prop="order_sn"></el-table-column>
        <el-table-column label="拼课订单数" prop="order_count"></el-table-column>
        <el-table-column label="订单金额" prop="order_money"></el-table-column>
        <el-table-column label="结算金额" prop="pay_money"></el-table-column>
        <el-table-column label="收款人" prop="card_holder"></el-table-column>
        <el-table-column label="收款账户" prop="card_number"></el-table-column>
        <el-table-column label="结算状态">
          <template slot-scope="scope">
            <template v-if="scope.row.status / 1 === 0 ">结算中
              <br>预计7个工作日到账
            </template>
            <template v-else-if="scope.row.status / 1 === 2 ">已结算
              <br>注意查收
            </template>
            <template v-else>结算失败</template>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toDetails(scope.row)">查看订单明细</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <div class="pub-form-wrap" v-show="pageType===1">
      <el-form
        ref="form"
        :model="formData"
        label-width="120px"
        class="pub-form"
        :rules="formRules"
        v-loading="formLoading"
      >
        <el-form-item label="结算方式">
          <el-radio @change="funChange" v-model="formData.type" label="1">银行卡结算</el-radio>
          <el-radio @change="funChange" v-model="formData.type" label="2">微信零钱包结算</el-radio>
        </el-form-item>
        <!-- 银行卡结算 -->
        <template v-if="formData.type/1 === 1">
          <el-form-item label="收款人" prop="card_holder">
            <el-input v-model="formData.card_holder" placeholder="请输入收款人姓名"></el-input>
          </el-form-item>
          <el-form-item label="收款账户" prop="card_number">
            <el-input v-model="formData.card_number" placeholder="请输入收款账户"></el-input>
          </el-form-item>
          <el-form-item label="开户银行" prop="bank_name">
            <el-input v-model="formData.bank_name" placeholder="请输入开户银行"></el-input>
          </el-form-item>
        </template>
        <!-- 微信零钱包结算 -->
        <template v-else-if="!noPremission">
          <el-form-item label="收款人" prop="card_holder">
            <el-input v-model="formData.card_holder" placeholder="姓名"></el-input>
          </el-form-item>
          <el-form-item label="身份证号码" prop="id_card_number">
            <el-input v-model="formData.id_card_number" placeholder="身份证号码"></el-input>
          </el-form-item>
          <el-form-item label="收款微信">
            <template slot-scope="scope">
              <template v-if="walletInfo && walletInfo.is_bind / 1 === 0">
                <qrcode :value="walletInfo.bind_url" :options="{ size: 170 }"></qrcode>
              </template>
              <template v-if="walletInfo && walletInfo.is_bind / 1 === 1">
                <p class="bind-title">
                  <span>已绑定</span>
                  <el-button @click="cancleBind" class="cancle-btn" type="text">取消绑定</el-button>
                </p>
                <div class="bind-img-wrap">
                  <img :src="walletInfo.bind_info.head_image">
                </div>
                <p class="bind-name">微信昵称:{{walletInfo.bind_info.nick_name}}</p>
              </template>
            </template>
          </el-form-item>
        </template>
        <span class="tips" v-else>微信零钱包结算暂无权限</span>
      </el-form>
      <div v-if="!noPremission" class="pub-form-submit-bar">
        <el-button type="primary" @click="submitForm">保存</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import {
  getAccountCheckList,
  getAccountInfo,
  createAccount,
  updateAccount,
  createAccountList,
  getWalletInfo,
  unbindWx
} from "@/api/group_course";
import VueQrcode from "@xkeshi/vue-qrcode";
import pubLoadingWrap from "@/components/pub_loading_wrap";
import radioBar from "@/components/top_box/radio_bar";
import tagsBar from "@/components/top_box/tags_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      pageType: 0,
      listLoading: false,
      listData: [],
      accountLoading:false,
      dataLoading: true,
      formData: {
        card_holder: "",
        card_number: "",
        bank_name: "",
        id_card_number: "",
        type: 1
      },
      formRules: {
        card_holder: [{ required: true, message: "请输入收款人姓名", trigger: "blur" }],
        card_number: [{ required: true, message: "请输入收款账号", trigger: "blur" }],
        bank_name: [{ required: true, message: "请输入银行名称", trigger: "blur" }],
        id_card_number: [{ required: true, message: "请输入身份证号码", trigger: "blur" }]
      },
      page: 1,
      size: 10,
      count: 0,
      formLoading: false,
      isEdit: false,
      is_new: 0,
      listType: [{ label: "拼课", value: 0 }, { label: "红包拼课", value: 1 }],
      walletInfo: null,
      timer: null,
      detailList: [],
      accountShow: false,
      noPremission: false, //微信零钱包权限
      tagsArr: [{ text: "结算订单", value: 0 }, { text: "结算方式", value: 1 }],
      toAccountText: "没有可结算的订单"
    };
  },
  components: {
    "v-loading-wrap": pubLoadingWrap,
    "v-radio-bar": radioBar,
    qrcode: VueQrcode,
    "v-tag-bar": tagsBar,
    "v-table-wrap": tableTemplate
  },
  activated() {
    clearInterval(this.timer);
    this.is_new = 0;
    if (this.pageType === 0) {
      this.getList();
    } else if (this.pageType === 1) {
      this.getAccountDetails();
    }
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    cancleBind() {
      this.$confirm("确定取消绑定吗")
        .then(res => {
          console.log("res", res);
          return unbindWx();
        })
        .then(res => {
          if (res) {
            this.$message.success("解绑成功");
            this.getWalletInfo();
          }
        })
        .catch(e => {
          if (e !== "cancel") this.$messag.error(e);
        });
    },
    funChange(val) {
      if (val / 1 === 2) {
        this.getWalletInfo();
      } else {
        clearInterval(this.timer);
      }
    },
    showAccountDetails() {
      this.detailList = [];
      this.accountLoading = true;
      createAccountList({
        page: this.page,
        size: this.size,
        is_new: this.is_new / 1 === 1 ? true : false,
        is_check: 0
      })
        .then(res => {
          let {
            real_name,
            order_amount,
            service_fee,
            pay_money,
            type,
            card_number,
            nick_name
          } = res.data;
          type = type / 1;
          this.detailList = [
            { label: "申请人", data: real_name, show: true },
            { label: "订单总额", data: order_amount, show: true },
            { label: "手续费", data: service_fee, show: true },
            { label: "结算金额", data: pay_money, show: true },
            {
              label: "结算方式",
              data: type === 0 ? "结算至银行账户" : "结算至微信零钱包",
              show: true
            },
            { label: "银行卡号", data: card_number, show: type === 0 },
            { label: "收款微信号-昵称", data: nick_name, show: type === 1 }
          ];
          this.accountLoading  = false;
        })
        .catch(e => {
          console.log("error", e);
          this.accountLoading  = false;
          if (typeof e === "string") this.toAccountText = e;
        });
    },
    submitOrder() {
      createAccountList({
        page: this.page,
        size: this.size,
        is_new: this.is_new / 1 === 1 ? true : false,
        is_check: 1
      })
        .then(res => {
          console.log(res);
          this.getList();
          this.$message.success("生成结算订单成功");
          this.accountShow = false;
        })
        .catch(e => {
          console.log("error", e);
          this.$message.error(e);
        });
    },
    setTimer() {
      this.timer = setInterval(() => {
        if (this.walletInfo && this.walletInfo.is_bind / 1 === 1) {
          clearInterval(this.timer);
        } else {
          getWalletInfo()
            .then(res => {
              console.log("xq", res);
              this.walletInfo = res.data;
            })
            .catch(e => {
              console.log("e", e);
            });
        }
      }, 1000);
    },
    getWalletInfo() {
      getWalletInfo()
        .then(res => {
          this.walletInfo = res.data;
          this.setTimer();
        })
        .catch(e => {
          console.log("e", e);
          this.noPremission = true;
        });
    },
    typeChange(val) {
      if (this.pageType == val) {
        return;
      } else {
        this.pageType = val ? val : 0;
      }
      clearInterval(this.timer);
      this.is_new = 0;
      if (this.pageType === 0) {
        this.getList();
      } else if (this.pageType === 1) {
        this.getAccountDetails();
      }
    },
    getAccountDetails() {
      clearInterval(this.timer);
      getAccountInfo({})
        .then(res => {
          if (res.data) {
            this.isEdit = true;
            this.formData = res.data;
            if (res.data.type == 2) {
              this.getWalletInfo();
            }
          } else {
            this.isEdit = false;
            this.formData = {
              card_holder: "",
              card_number: "",
              bank_name: "",
              id_card_number: "",
              type: "1"
            };
          }
        })
        .catch(e => {
          console.log(e);
        });
    },
    getList() {
      let obj = {
        page: this.page,
        count: this.size,
        type: this.is_new / 1 === 1 ? 4 : 1
      };
      this.listLoading = true;
      getAccountCheckList(obj)
        .then(res => {
          console.log("res", res);
          this.count = Number(res.data.count);
          this.listData = res.data.list;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    toDetails(item) {
      this.$router.push({
        name: "group_accounting_center_details",
        query: { id: item.id, type: this.is_new }
      });
    },
    submitForm() {
      this.$refs.form
        .validate()
        .then(res => {
          if (this.formData.type / 1 === 2 && this.walletInfo.is_bind / 1 === 0) {
            this.$message.error("请先绑定收费微信");
            return;
          }
          let obj = {
            type: this.formData.type,
            card_holder: this.formData.card_holder
          };
          if (this.isEdit) obj.id = this.formData.id;
          if (this.formData.type / 1 === 1) {
            obj.card_number = this.formData.card_number;
            obj.bank_name = this.formData.bank_name;
          } else {
            obj.id_card_number = this.formData.id_card_number;
          }
          return this.isEdit ? updateAccount(obj) : createAccount(obj);
        })
        .then(res => {
          if (res) {
            this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
            this.getWalletInfo();
          }
        })
        .catch(e => {
          if (e === false) {
            this.$message.error("请输入必填项");
            return;
          }
          console.log("error", e);
          this.$message.error(e);
        });
    }
  },
  deactivated() {
    clearInterval(this.timer);
  }
};
</script>


<style lang="stylus" scoped>
.tips-text
  // padding-left: 30px;
  margin-top: 10px;
  line-height: 18px;
.bind-title
  font-size: 24px;
  margin-left: 20px;
  .cancle-btn
    margin-left: 60px;
.bind-img-wrap
  margin-top: 20px;
  margin-left: 20px;
  width: 132px;
  height: 132px;
  overflow: hidden;
  border-radius: 50%;
.bind-name
  font-size: 24px;
  margin-left: 20px;
  margin-top: 20px;
.account-details
  .details-row
    display: flex;
    text-align: right;
    margin-bottom: 10px;
    .label
      margin-right: 20px;
      color: #111;
      flex: 0 0 110px;
    .data
      color: #999;
.tips-content
  margin-top: 20px;
  padding: 0 20px;
  text-align: justify;
.submit-btn
  margin-top: 20px;
  margin-left: 20px;
.tips
  margin-left: 40px;
  font-size: 24px;
  color: #999;
</style>



