import request from '@/utils/request'

// 创建银行卡信息
export function createBankInfo(data) {
  return request('educrm/balance/create', data)
}

//获取银行卡信息
export function getBankInfo(data) {
  return request('educrm/balance/view', data)
}

// 修改银行卡信息
export function updateBankInfo(data) {
  return request('educrm/balance/update', data)
}

//获取转账记录
export function getBalanceRecordList(data) {
  return request('educrm/balance/get-record-list', data)
}



//钱包余额-获取学生钱包变化记录列表

export function getBalanceList(data) {
  return request("educrm/student/balance-list", data);
}

//钱包余额-提现申请
export function toWithdraw(data) {
  return request("educrm/balance-record/apply", data);
}

//钱包余额-获取退款记录表
export function getRefundList(data) {
  return request("educrm/balance-record/list", data);
}

//钱包余额-提现同意或拒绝
export function handleRefund(data) {
  let str = "educrm/balance-record/succeed";
  // 0 拒绝 1 同意
  if (data.type == 0) {
    str = "educrm/balance-record/failed"
  }
  delete data.type;
  return request(str, data);
}

//钱包余额 - 获取钱包列表
export function getPurseList(data) {
  return request("educrm/student/get-balance-list", data);
}

//钱包余额-结课记录
export function getFinishList(data) {
  return request("educrm/finance/closing-record", data);
}