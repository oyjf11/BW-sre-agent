import request from '@/utils/request'

// 订单列表
export function getOrderData (page, count, search, start_date, end_date, type = 0) {

	let org_name = search.org_name;
  return request('educrm/organization/order-data', {page,count,org_name, start_date, end_date, type})
}

// 提交审核申请
export function apply (data) {
  return request('educrm/finance-apply/apply', data)
}

//重新提交审核申请
export function reapply (data) {
  return request('educrm/finance-apply/reapply', data)
}

//失败审核申请
export function failed (data) {
  return request('educrm/finance-apply/failed', data)
}

//成功审核申请 
export function succeed (data) {
  return request('educrm/finance-apply/succeed', data)
}

//撤销审核申请
export function cancel (data) {
  return request('educrm/finance-apply/failed', data)
}

//列表
export function list (data) {
  return request('educrm/finance-apply/list', data)
}

//预收表导出
export function exportTable(data){
  return request('educrm/deliver/course-split', data)
}
// 打印
export function postPrint(data){
  return request('educrm/order/yly-print', data)
}
// 测试打印
export function testPostPrint(data){
  return request('educrm/order/test', data)
}
