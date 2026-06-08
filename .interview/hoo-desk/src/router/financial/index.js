import _layout from "@/views/layout/layout.vue";
/**
 * 财务结算 路由模块
 */
//缴费记录
const PaymentRecords = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/recruit_student/payment_records.vue");
//缴费对账
const AccountCheck = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/account_checking.vue");
//对账记录
const CheckingOperatiorsList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/checking_operatiors_list.vue");
//缴费对账
const Audit = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/audit.vue");
//在线订单缴费对账
const OnlineAccountCheck = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/online_account_checking");
//申述审核
const FinanceApplyList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/apply/list.vue");
//退款记录
const RefundList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/refund_list.vue");
//待退款记录
const UnRefundList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/unrefund_list.vue");
//钱包记录
const PurseList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/purse_list.vue");
//结课记录
const FinishList = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/finish_list.vue");
//余额明细
const BalanceDetail = () =>
  import(/* webpackChunkName: "group-financial" */ "@/views/financial/balance_detail.vue");
/**
 * 路由模块end
 */

let router = {
  name: "financial",
  text: "财务中心",
  path: "/financial",
  icon: "hoo hoo-integral icon-lg",
  newicon:"hoo hoo-integral_fill icon-lg",
  component: _layout,
  meta: { power: ["financial"] },
  children: [
    {
      name: "account_checking",
      text: "缴费对账",
      path: "/financial/account_checking",
      meta: {
        power: ["account_checking"],
        title: "缴费对账",
        keepAlive: true
      },
      component: AccountCheck
    },
    
    {
      name: "checking_operatiors_list",
      text: "对账记录",
      path: "/financial/checking_operatiors_list",
      newShow:false,
      meta: {
        power: ["account_checking"],
        title: "对账记录"
      },
      component: CheckingOperatiorsList
    },
    {
      name: "audit",
      hide: true,
      path: "/financial/audit",
      meta: {
        power: ["financial_audit"],
        title: "缴费数据",
        des:"实现快速缴费，查看订单金额、课程、缴费状态等。"
      },
      component: Audit
    },
    {
      name: "miniprogram_payment",
      hide: true,
      path: "/financial/miniprogram_payment",
      meta: { 
        // power: ['miniprogram_payment'] 
        keepAlive:true,
        title:"对账记录",
      },
      component: PaymentRecords
    },
    {
      name: "finance_apply_list",
      text: "申诉审核",
      path: "/financial/apply/list",
      meta: {
        power: ["account_checking"],
        title: "申诉审核"
      },
      component: FinanceApplyList
    },
    {
      name: "online_account_checking",
      text: "小程序对账",
      path: "/financial/online_account_checking",
      meta: {
        power: ["account_checking"],
        title: "小程序对账",
        keepAlive: true
      },
      component: OnlineAccountCheck
    },
    {
      name: "refund_list",
      hide: true,
      path: "/financial/refund_list",
      meta: { power: ["financial_audit"],  title: "退款列表",},
      component: RefundList
    },
    {
      name: "unrefund_list",
      hide: true,
      path: "/financial/unfund_list",
      meta: {
        power: ["financial_audit"],
        title: "未退款列表",
      },
      component: UnRefundList
    },
    {
      name: "purse_list",
      hide: true,
      path: "/financial/purse_list",
      meta: { power: ["financial_audit"], title: "钱包记录",},
      component: PurseList
    },
    {
      name: "finish_list",
      hide: true,
      path: "/financial/finish_list",
      meta: { power: ["financial_audit"], title: "结课记录",},
      component: FinishList
    },
    {
      name: "balance_detail",
      text: "余额明细",
      path: "/financial/balance_detail",
      hide: true,
      meta: {
        power: ["account_checking"],
        title: "余额明细",
        keepAlive: true
      },
      component: BalanceDetail
    },
  ]
};

export default router;
